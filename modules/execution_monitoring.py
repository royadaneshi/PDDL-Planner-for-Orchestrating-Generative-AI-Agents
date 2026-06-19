import networkx as nx
import pandas as pd
import variables
from pddl_helpers.update_pddl_model import model_repair
from tools.get_booked_items import get_booked_names, get_booked_items, get_obj_type
from tools.get_updated_plan import get_plan
from variables import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def check_plan_match():
    logger.info(F"{'_' * 10}\t Checking whether booked items match the plan...")
    get_plan()
    plan = variables.ORCHESTRATION_PLAN.split("\n")
    for booked_item in get_booked_names(variables.BOOKED_ITEMS):
        booked_item_type = [obj.type_tag for obj in PDDL_PROBLEM.objects if str(obj.name).lower() == booked_item][0]
        for plan_item in plan:
            item_identifier = plan_item.split()[1]
            plan_type = [obj.type_tag for obj in PDDL_PROBLEM.objects if str(obj.name).lower() == item_identifier][0]
            if plan_type == booked_item_type:
                if item_identifier != booked_item:
                    return False, booked_item

    return True, None


def get_same_type_item(item):
    obj_type = get_obj_type(item)
    variables.BOOKED_ITEMS = get_booked_items()
    equivalent_item = [i for i in variables.BOOKED_ITEMS if get_obj_type(i[0]) == obj_type]
    if equivalent_item:
        return equivalent_item[0]
    else:
        return None


async def check_booked_items_feasibility():
    """
    check if the booked items timing are feasible so far, if was a problem return unachievable if not return ok
    for this fixe the booked items and run teh planner , if gave a plan then it is feasible if not then not feasible
    Caution:We assume that the second parameter on the actions in the pddl model is the time corresponds to that item
        that being booked in that action.
    """
    logger.info(F"{'_' * 10}\t Checking booked items timing feasibility...")
    links = variables.CASUAL_LINK
    variables.BOOKED_ITEMS = get_booked_items()
    actions = []
    for link in links:
        if link["producer"] != "__init__":
            actions.append(link)

    dependency_graph = nx.DiGraph()
    booked_types = [get_obj_type(item) for item in get_booked_names(variables.BOOKED_ITEMS)]

    for action in actions:
        node_a = (action['producer'].split(' ')[1], action['producer'].split(' ')[2])
        node_b = (action['consumer'].split(' ')[1], action['consumer'].split(' ')[2])
        if get_obj_type(node_b[0]) in booked_types and get_obj_type(node_a[0]) in booked_types:
            if node_a in variables.BOOKED_ITEMS:
                a = node_a
            else:
                a = get_same_type_item(node_a[0])
            if node_b in variables.BOOKED_ITEMS:
                b = node_b
            else:
                b = get_same_type_item(node_b[0])
            if a and b:
                dependency_graph.add_edge(a, b, fact=action['fact'])

    logger.info(f"Dependency graph: {dependency_graph.edges}")
    for edge in dependency_graph.edges():
        producer = str(edge[0][1]).strip('t')
        consumer = str(edge[1][1]).strip('t')
        producer_time = pd.to_datetime(producer, format='%H-%M').time()
        consumer_time = pd.to_datetime(consumer, format='%H-%M').time()
        if producer_time > consumer_time:
            return False
    return True


async def execution_monitoring():
    """
    this is the start point of the EM, if any of two case of the problem happened we repair it here
    and return only runs the next booking item
    """
    logger.info(f"{'__' * 70}")
    logger.info(f"Starting the Execution Monitoring ...")

    booked_items = get_booked_items()
    last_booked_item = booked_items[-1]
    feasibility_result = await check_booked_items_feasibility()
    if not feasibility_result:
        logger.info(f"\n \t {'X ' * 30} PLAN UNACHIEVABLE found on {last_booked_item} {'X ' * 30}\n")
        await model_repair(PLAN_UNACHIEVABLE, last_booked_item)
    else:
        plan_match = check_plan_match()
        if plan_match[0]:
            logger.info(f"{'~*~' * 50}")
            logger.info(
                f"\t Execution Monitoring check passed! (No plan contradiction or unachievable plan detected.")
            logger.info(f"{'~*~' * 50}\n")
        else:
            logger.info(f"\n \t {'X ' * 30} PLAN CONTRADICTION found on {plan_match[1]} {'X ' * 30}\n")
            await model_repair(PLAN_CONTRADICTION, None)
