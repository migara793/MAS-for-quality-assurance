import os

import asyncio
import logging
import json
import uvicorn
import time
from contextlib import asynccontextmanager
from typing import List, Any, Dict, Optional, Type, AsyncGenerator, Set
from pydantic import BaseModel, ValidationError
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from app_utils.env import config
from tools.mcp_config import get_mcp_tools, filter_tools_by_name
from tools.retriever import tool_retriever
from app.agent import root_agent, generation_agent, execute_agent, optimize_agent, report_agent

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(name)s: %(message)s')
logger = logging.getLogger('QA-Pipeline-Monitor')

# Persistent state
SYSTEM_STATE = {
    "ready": False,
    "status": "Initializing tools...",
    "tools_count": 0,
    "logs": []
}

DEFAULT_MISSION = (
    "Perform a full autonomous QA audit on the current codebase. "
    "1. Unit Testing: Discover, run, and fix any failing unit tests. "
    "2. Integration Testing: Verify interactions between components and services. "
    "3. E2E Testing: Verify core UI flows using Playwright. "
    "4. Security: Audit for common vulnerabilities. "
    "5. Performance: Identify and report performance bottlenecks. "
    "6. Reporting: Generate a comprehensive QA_REPORT.md summary."
)

event_subscribers: Set[asyncio.Queue] = set()

async def broadcast_event(message: str, event_type: str = 'log'):
    payload = {
        'message': message, 
        'type': event_type, 
        'time': time.strftime("%H:%M:%S", time.localtime())
    }
    SYSTEM_STATE["logs"].append(payload)
    if len(SYSTEM_STATE["logs"]) > 500: SYSTEM_STATE["logs"] = SYSTEM_STATE["logs"][-500:]
    
    if event_subscribers:
        for q in event_subscribers:
            await q.put(payload)

session_service = InMemorySessionService()
app_name = 'QA-Swarm'

async def initialize_tools():
    try:
        all_tools = await get_mcp_tools()
        
        # 1. Index all tools into Qdrant for semantic retrieval
        await tool_retriever.index_tools(all_tools)
        
        # 2. Dynamically assign tools based on agent roles/instructions
        # Test Generation Agent: Needs tools for code analysis and file writing
        generation_agent.tools = await tool_retriever.retrieve_tools(
            "Read codebase files, list directories, search files, and write new test files or edit/update existing code.",
            all_tools,
            top_k=12
        )
        
        # Test Execution Agent: Needs tools for running shell commands and browser automation
        execute_agent.tools = await tool_retriever.retrieve_tools(
            "Execute shell commands, run tests, edit files if needed to fix test scripts, and use browser automation/playwright to verify UI flows.",
            all_tools,
            top_k=15
        )
        
        # Optimization Agent: Needs tools for fixing code and executing shell commands
        optimize_agent.tools = await tool_retriever.retrieve_tools(
            "Patch and edit existing code files, fix bugs, search repositories, and run shell commands to verify fixes.",
            all_tools,
            top_k=12
        )
        
        # Report Generator Agent: Needs tools for reading files and writing reports
        report_agent.tools = await tool_retriever.retrieve_tools(
            "Read test results, list directories, and read file contents to generate a comprehensive markdown report.",
            all_tools,
            top_k=8
        )
        
        SYSTEM_STATE["ready"] = True
        SYSTEM_STATE["status"] = "Ready"
        SYSTEM_STATE["tools_count"] = len(all_tools)
        logger.info(f'STATUS: Discovery Complete. {len(all_tools)} tools active.')
        await broadcast_event(f"✅ System Ready: {len(all_tools)} tools discovered and indexed for Semantic Retrieval.", "success")
    except Exception as e:
        SYSTEM_STATE["status"] = f"Init Error: {str(e)}"
        await broadcast_event(f"❌ System Init Failed: {str(e)}", "error")

async def run_pipeline(request: str):
    await broadcast_event(f'🚀 PIPELINE TRIGGERED: {request}', 'system')
    runner = Runner(app_name=app_name, agent=root_agent, session_service=session_service)
    session = await session_service.create_session(app_name=app_name, user_id='default_user')
    message = types.Content(role='user', parts=[types.Part(text=request)])
    
    current_agent = None
    step_count = 0
    MAX_STEPS = 50  # Hard limit on tool calls/agent switches
    TIMEOUT_SECONDS = 600  # 10 minute hard timeout
    start_time = time.time()
    
    try:
        async for event in runner.run_async(session_id=session.id, user_id='default_user', new_message=message):
            # Check for timeout
            if time.time() - start_time > TIMEOUT_SECONDS:
                logger.error("Pipeline TIMEOUT reached.")
                await broadcast_event("⚠️ PIPELINE TIMEOUT: Process took too long and was terminated.", "error")
                break

            # Check for max steps
            step_count += 1
            if step_count > MAX_STEPS:
                logger.error("Pipeline MAX STEPS reached.")
                await broadcast_event("⚠️ PIPELINE LIMIT REACHED: Too many steps, terminating to prevent loop.", "error")
                break

            agent_name = getattr(event, 'author', None)
            if agent_name == 'user': agent_name = None
            
            if not agent_name and hasattr(event, 'node_info') and event.node_info and event.node_info.path:
                path_parts = event.node_info.path.split('/')
                if path_parts: agent_name = path_parts[-1].split('@')[0]
            
            if not agent_name:
                if hasattr(event, 'agent') and event.agent: agent_name = getattr(event.agent, 'name', None)
                if not agent_name: agent_name = getattr(event, 'agent_name', None)
            
            if not agent_name and hasattr(event, 'get_agent_name'): agent_name = event.get_agent_name()
                
            if agent_name and agent_name != current_agent:
                current_agent = agent_name
                await broadcast_event(f'👤 AGENT ACTIVE: [{agent_name}]', 'agent')
                logger.info(f'Detected Agent Switch: {agent_name}')

            payload_agent = agent_name or current_agent or "Unknown"

            if hasattr(event, 'get_function_calls') and event.get_function_calls():
                for call in event.get_function_calls():
                    await broadcast_event(f'🛠️  {payload_agent}: [{call.name}]', 'tool')
            if hasattr(event, 'get_function_responses') and event.get_function_responses():
                for resp in event.get_function_responses():
                    await broadcast_event(f'✅ {payload_agent}: [{resp.name}]', 'success')
        
        await broadcast_event('🏁 PIPELINE COMPLETED', 'system')
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        await broadcast_event(f"❌ PIPELINE ERROR: {str(e)}", "error")
        await broadcast_event('🏁 PIPELINE TERMINATED', 'system')

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(initialize_tools())
    yield

app = FastAPI(lifespan=lifespan)
if os.path.exists('static'): app.mount('/static', StaticFiles(directory='static'), name='static')

class TaskRequest(BaseModel): request: Optional[str] = None

@app.get('/')
async def read_index(): return FileResponse('static/index.html') if os.path.exists('static/index.html') else {'error': 'UI not found'}

@app.get('/health')
async def health(): return SYSTEM_STATE

@app.post('/run')
async def trigger_run(background_tasks: BackgroundTasks, task: Optional[TaskRequest] = None):
    mission = (task.request if task and task.request else None) or DEFAULT_MISSION
    background_tasks.add_task(run_pipeline, mission)
    return {'status': 'Processing', 'mission': mission}

@app.post('/webhook/github')
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    # This endpoint is designed to be called by GitHub Actions or Webhooks
    background_tasks.add_task(run_pipeline, DEFAULT_MISSION)
    await broadcast_event("🔔 GITHUB PUSH DETECTED: Triggering CI/CD Pipeline", "system")
    return {'status': 'Triggered CI/CD Pipeline'}

@app.get('/events')
async def event_stream(request: Request):
    q = asyncio.Queue()
    for log in SYSTEM_STATE["logs"]: await q.put(log)
    event_subscribers.add(q)
    async def gen():
        try:
            while True:
                if await request.is_disconnected(): break
                try:
                    ev = await asyncio.wait_for(q.get(), timeout=1.0)
                    yield f'data: {json.dumps(ev)}\n\n'
                except asyncio.TimeoutError: yield ': keep-alive\n\n'
        finally: event_subscribers.remove(q)
    return StreamingResponse(gen(), media_type='text/event-stream')

@app.get('/agents')
async def list_agents():
    return {'agents': [
        {'name': 'QAOrchestrator', 'role': 'Root', 'tools': []},
        {'name': 'TestGenerationAgent', 'role': 'Dev', 'tools': [t.name for t in generation_agent.tools]},
        {'name': 'TestExecutionAgent', 'role': 'DevOps', 'tools': [t.name for t in execute_agent.tools]},
        {'name': 'OptimizationAgent', 'role': 'Architect', 'tools': [t.name for t in optimize_agent.tools]},
        {'name': 'ReportGeneratorAgent', 'role': 'Reporter', 'tools': [t.name for t in report_agent.tools]}
    ]}

@app.get('/report')
async def get_report():
    report_path = 'QA_REPORT.md'
    if os.path.exists(report_path):
        with open(report_path, 'r') as f: return {'content': f.read()}
    return {'error': 'Report not found'}

if __name__ == '__main__': uvicorn.run(app, host='0.0.0.0', port=8000)
