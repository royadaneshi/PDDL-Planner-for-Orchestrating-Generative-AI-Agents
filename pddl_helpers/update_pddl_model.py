import logging
import variables
from agents.predicate_searcher_agent import run_predicate_searcher_agent
from pddl_helpers.pddl_planner import PDDL_Planner
from tools.update_booked_items import update_booked_items
from variables import PLAN_UNACHIEVABLE, PDDL_PLAN_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def model_repair(error_type, violated_item):
    """
    We consider the last booked item is the one causing an issue
    in case of PLAN_UNACHIEVABLE: remove the contradicted item and fix the other booked items and replan
    In case of PLAN_CONTRADICTION: fix the contradicted item and the other booked items and replan
    """
    logger.info(f"{'_' * 10}\t Updating PDDL model and replanning...")

    if error_type == PLAN_UNACHIEVABLE:
        # remove the unachievable item from the booked items, and the pddl model initials
        update_booked_items(violated_item)

    # run predicate_searcher agent to get the predicates for the valid booked items
    variables.PLAN_UPDATED = False
    if len(variables.BOOKED_ITEMS) > 0:
        while not variables.PLAN_UPDATED:
            await run_predicate_searcher_agent()

        variables.PLAN_UPDATED = False
    replanning()


def replanning():
    logger.info(f"{'_' * 10}\t Replanning, based on the current state and booked items so far ... \n")

    planner = PDDL_Planner()
    planner.run_fd()
    with open(PDDL_PLAN_PATH, "r") as f:
        variables.ORCHESTRATION_PLAN = f.read()

    logger.info(f"{'_' * 10}\t New plan achieved: {variables.ORCHESTRATION_PLAN}")
    logger.info(f"{'_' * 10}\t Continue the planning...")
