import logging
import variables
from agents.booking_agent import selection_booking
from modules.call_agent import call_agent_async, setup_session_and_runner
from modules.execution_monitoring import execution_monitoring
from pddl_helpers.update_pddl_model import model_repair, replanning
from tools.get_booked_items import get_booked_names, get_obj_type
from tools.get_session import get_current_session
from tools.get_updated_plan import get_plan
from variables import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean():
    # plan should be found each time newly
    variables.PDDL_PROBLEM = parse_problem(PDDL_PROBLEM_PATH)
    if os.path.exists(PDDL_PLAN_PATH):
        os.remove(PDDL_PLAN_PATH)
        logger.info(f"Orchestration plan file removed successfully.")


def get_current_booking_item():
    """
    Consider the first parameter is the booking item after the action name:
    (book-flight fr740 flight-agent denver chicago c99 t06-00 t08-35 c35)
    """
    get_plan()
    plan = variables.ORCHESTRATION_PLAN.split("\n")
    if not plan:
        return "All items have been booked."
    current_session = get_current_session()
    for item in plan:
        if item.split()[1] not in get_booked_names(variables.BOOKED_ITEMS):
            variables.CURRENT_OBJECT_TO_BOOK = item.split()[1]
            obj_type = get_obj_type(variables.CURRENT_OBJECT_TO_BOOK)
            current_session.state[CURRENT_OBJECT_TO_BOOK_KEY] = {TYPE: obj_type,
                                                                 OBJECT: variables.CURRENT_OBJECT_TO_BOOK}
            return item.split()[1]

    return "All items have been booked."


async def orchestration():
    logger.info("Hey! I'm your travel organizer. Starting the orchestration...")
    user_input = "Follow the system prompt to complete your assigned tasks. Use the given tool outputs, and do not refer to results from previous turns, as they may be outdated."
    logger.info("Starting the planning...")
    session_service, runner = await setup_session_and_runner(selection_booking)
    variables.SESSION_SERVICE = session_service
    plan_action = variables.ORCHESTRATION_PLAN.split("\n")
    while len(variables.BOOKED_ITEMS) < len(plan_action):
        variables.REPLAN_FLAG = False
        booking_result = get_current_booking_item()
        if booking_result == "All items have been booked.":
            break
        logger.info(f"_____________ Current item to book: {variables.CURRENT_OBJECT_TO_BOOK}")
        SUCCESSFUL_BOOKING[0] = False
        SUCCESSFUL_BOOKING[1] = f"{get_obj_type(variables.CURRENT_OBJECT_TO_BOOK)} has not booked yet."
        await call_agent_async(user_input, runner, session_service)
        if SUCCESSFUL_BOOKING[0]:
            await execution_monitoring()
        if variables.REPLAN_FLAG:
            logger.info(f"Replanning ...")
            if len(variables.BOOKED_ITEMS) > 0:
                await model_repair(PLAN_UNACHIEVABLE, variables.BOOKED_ITEMS[-1])
            else:
                replanning()
        if not SUCCESSFUL_BOOKING[0]:
            logger.info(f"{SUCCESSFUL_BOOKING[1]}")
            logger.info(f"Reprompting the booking agent ...")

        current_session = get_current_session()
        variables.BOOKED_ITEMS = current_session.state.get(variables.STATE, [])

    variables.ORCHESTRATION_RESULT = "FINISHED_travel_planning"
    current_session = get_current_session()
    variables.BOOKED_ITEMS = current_session.state.get(STATE, [])
    logger.info("\n")
    logger.info(" ~**~" * 30)
    logger.info(" ~**~" * 30)
    logger.info("\n")
    logger.info(f"\t \t Orchestration complete. Travel plan successfully booked.\n")
    logger.info(f"\t \t Booked Items: {variables.BOOKED_ITEMS}")
    logger.info("\n")
    logger.info(" ~**~" * 30)
    logger.info(" ~**~" * 30)
    logger.info("\n")

    clean()
