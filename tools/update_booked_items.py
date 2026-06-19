from pddl.core import Problem
from tools.get_session import get_current_session
from tools.update_budget import update_budget
from variables import *
import variables
from pddl_helpers.pddl_planner import logger


def update_booked_items(violated_item):
    """
    In this function, we update the booked items so far. If there is an item that makes the plan unachievable,
    remove it so the agent can book it again using a new plan.
    """
    current_session = get_current_session()
    current_bookings = current_session.state.get(STATE, [])
    updated_bookings = []
    for item in current_bookings:
        if violated_item != item:
            updated_bookings.append(item)
        else:
            revert_pddl_model(violated_item)
            update_budget(violated_item, current_session, False)

    current_session.state[STATE] = updated_bookings
    previous_violated_items = current_session.state.get(VIOLATED, [])
    previous_violated_items.append(violated_item)
    current_session.state[VIOLATED] = previous_violated_items
    logger.info(f"{'_' * 10}\t Updated booked items: {updated_bookings}")


def revert_pddl_model(violated_item):
    logger.info(f"{'_' * 10}\t Reverting PDDL model for {violated_item}...")
    problem = parse_problem(PDDL_PROBLEM_PATH)

    current_init = set(problem.init)
    if violated_item[0] in variables.PREDICATE_PER_ITEM.keys():
        for predicate in variables.PREDICATE_PER_ITEM[violated_item[0]]:
            if predicate in current_init:
                current_init.remove(predicate)

        variables.UPDATED_INIT = current_init

        pddl_problem = parse_problem(PDDL_PROBLEM_PATH)
        variables.PDDL_PROBLEM = Problem(
            name=pddl_problem.name,
            domain_name=pddl_problem.domain_name,
            objects=pddl_problem.objects,
            init=variables.UPDATED_INIT,
            goal=pddl_problem.goal,
            requirements=pddl_problem.requirements
        )
        with open(PDDL_PROBLEM_PATH, "w") as f:
            f.write(str(variables.PDDL_PROBLEM))
