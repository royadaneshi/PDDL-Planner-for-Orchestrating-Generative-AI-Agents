"""
In this  function we call the agents
"""
import logging
from dotenv import load_dotenv
from google.adk.apps import App
import variables
from variables import *
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

from variables import APP_NAME, USER_ID, SESSION_ID, STATE, EXECUTION_HISTORY, ORCHESTRATION_RESULT_KEY

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()


async def call_agent_async(user_input_prompt: str, runner: Runner, session_service: InMemorySessionService):
    current_input = user_input_prompt
    async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=types.Content(role='user',
                                      parts=[types.Part(text=current_input)]) if current_input else None
    ):

        variables.PDDL_PROBLEM = parse_problem(PDDL_PROBLEM_PATH)
        if event.content and event.content.parts:
            text_response = event.content.parts[0].text
            if text_response:
                logger.info("\n")
                logger.info(f"{'__' * 70}")
                logger.info(f"Response from [{event.author}]: {text_response}")

    session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    variables.BOOKED_ITEMS = session.state.get(STATE, [])
    logger.info("\n")
    logger.info(f"\t \t \t {'*' * 110}")
    logger.info(f"\t \t \t \t \t Booked Items So Far: {variables.BOOKED_ITEMS}")
    logger.info(f"\t \t \t {'*' * 110}")
    logger.info("\n")


async def setup_session_and_runner(agent):
    try:
        session = await variables.SESSION_SERVICE.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        variables.BUDGET = session.state.get(BUDGET_KEY)
        logger.info(f"Retrieved existing session.")
    except Exception:
        logger.info(f"Create new session.")

        session = await variables.SESSION_SERVICE.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        session.state[STATE] = []
        session.state[VIOLATED] = []
        session.state[EXECUTION_HISTORY] = []
        session.state[ORCHESTRATION_RESULT_KEY] = []
        session.state[BUDGET_KEY] = variables.BUDGET
        session.state[CURRENT_OBJECT_TO_BOOK_KEY] = {TYPE: "", OBJECT: ""}
        session.state[variables.ORCHESTRATION_PLAN_KEY] = variables.ORCHESTRATION_PLAN

    app_of_agent = App(
        name=APP_NAME,
        root_agent=agent,
    )
    runner = Runner(
        app=app_of_agent,
        session_service=variables.SESSION_SERVICE
    )

    return variables.SESSION_SERVICE, runner
