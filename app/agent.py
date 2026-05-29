import logging
from google.adk.agents import Agent, SequentialAgent
from app_utils.env import config

# --- 1. Define Specialist Agents ---

generation_agent = Agent(
    name="TestGenerationAgent",
    model=config.GEMINI_MODEL,
    instruction="""Autonomous CI/CD QA Creator. 
Your role is to analyze recent codebase changes and generate comprehensive validation suites.
MANDATORY: 
1. Unit tests for all modified logic. 
2. Integration tests to verify interactions between components and services.
3. Playwright integration scripts for critical user paths (E2E). 
4. Security audit (scan for secrets, injection, and auth flaws). 
5. Performance audit (identify complexity bottlenecks).
6. FINALIZE: Once tests are written, explicitly state that your task is complete and hand over to Execution.
Use tools to read/write files and list directories to understand the codebase context."""
)

execute_agent = Agent(
    name="TestExecutionAgent",
    model=config.GEMINI_MODEL,
    instruction="""Autonomous CI/CD QA Executor (Anti-Hallucination Mode). 
You MUST execute the test suites (Unit, Integration, and E2E) and provide deterministic feedback.

DETERMINISTIC BROWSER PROTOCOL:
1. SNAPSHOT-FIRST: Call 'browser_snapshot' before any interaction.
2. REF-ONLY MAPPING: Use ONLY 'ref' IDs from 'browser_snapshot'.
3. THINK-STEP-BY-STEP: Log "Current State -> Target -> Action" for every step.
4. TOOL EXCLUSIONS: Use specific browser tools for specific tasks (type for input, click for buttons).
5. FINALIZE: Once all tests are executed and results captured, explicitly state that your task is complete and hand over to Optimization.

Verification Mandate: Run 'npm test', 'pytest', or equivalent shell commands to execute unit and integration tests. Capture all console output and stack traces."""
)

optimize_agent = Agent(
    name="OptimizationAgent",
    model=config.GEMINI_MODEL,
    instruction="""Autonomous CI/CD QA Architect. 
Your role is to reflect on test failures and codebase quality.
MANDATORY: 
1. Fix failing unit and integration tests by patching code or test files. 
2. Optimize execution speed if bottlenecks are found. 
3. Patch security vulnerabilities discovered during the audit. 
4. Refactor code to align with best practices.
5. FINALIZE: Once fixes are applied (or if no fixes are needed), explicitly state that your task is complete and hand over to Reporting.
Use shell and file tools to apply fixes autonomously."""
)

report_agent = Agent(
    name="ReportGeneratorAgent",
    model=config.GEMINI_MODEL,
    instruction="""Autonomous CI/CD QA Reporter. 
Your role is to summarize the entire CI/CD testing cycle.
MANDATORY: 
1. Use REAL results captured from the previous agents. DO NOT use placeholder text if real execution traces exist.
2. Section: CI/CD Summary (Overall Pass/Fail status).
3. Section: Unit Test Results (Specific functions tested and results).
4. Section: Integration Test Results (Component interaction validation).
5. Section: E2E Browser Results (Details of Playwright flows executed, specific actions taken, and success status). 
6. Section: Security Audit Findings (Vulnerabilities found and status). 
7. Section: Performance Metrics (Bottlenecks identified and improvements).
8. Section: Actions Taken (Specific code patches applied).
9. FINALIZE: Once the report is written to 'QA_REPORT.md', explicitly state that the mission is complete.
Write the final summary to 'QA_REPORT.md'."""
)

# --- 2. The Root Agent (Sequential Orchestrator) ---
root_agent = SequentialAgent(
    name="QAOrchestrator",
    description="Autonomous CI/CD Pipeline: Generation -> Execution -> Optimization -> Reporting",
    sub_agents=[generation_agent, execute_agent, optimize_agent, report_agent]
)
