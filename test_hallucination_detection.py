import asyncio
import logging
from anti_hallucination_agent import anti_hallucination_agent
from google.adk.sessions import InMemorySessionService
from google.genai import types

async def test_hallucination():
    # Mocking the session and runner logic since we just want to test the agent response
    print("Testing Hallucination Detection...")
    
    test_cases = [
        "Proposed Tool Call: read_file(path='package.json'). Context: User wants to see dependencies.",
        "Proposed Tool Call: read_file(path='non_existent_config.yaml'). Context: Agent is guessing where the config might be.",
        "Proposed Tool Call: browser_click(selector='#submit-button-99'). Context: No snapshot taken yet, agent is guessing the ID."
    ]
    
    for case in test_cases:
        print(f"\n--- Testing Case ---\n{case}")
        try:
            # Note: anti_hallucination_agent.run might not be the correct method if it requires a Runner
            # We will try a simple way to get a response if possible, or use a Runner.
            from google.adk.runners import Runner
            session_service = InMemorySessionService()
            runner = Runner(app_name="Test", agent=anti_hallucination_agent, session_service=session_service)
            session = await session_service.create_session(app_name="Test", user_id="test_user")
            
            message = types.Content(role='user', parts=[types.Part(text=case)])
            async for event in runner.run_async(session_id=session.id, user_id='test_user', new_message=message):
                if hasattr(event, 'text') and event.text:
                    print(f"Agent Response: {event.text}")
        except Exception as e:
            print(f"Error testing case: {e}")

if __name__ == "__main__":
    asyncio.run(test_hallucination())
