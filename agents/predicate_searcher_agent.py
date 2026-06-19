from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, ToolContext
from pddl.core import Problem
from pddl.logic import Predicate, Constant
from modules.call_agent import setup_session_and_runner, call_agent_async
from tools.exit_tool import exit_loop
from tools.get_session import get_current_session
from variables import *
import variables
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_pddl():
    return f"Domain: {str(PDDL_DOMAIN)}\nProblem: {str(PDDL_PROBLEM)}"


def get_booked_items():
    logger.info(f"Getting booked items...")
    current_session = get_current_session()
    booked_items = current_session.state.get(STATE, [])
    return f"booked items: {booked_items}"


def update_pddl_model(tool_context: ToolContext, affected_predicates: dict[str, list[str]]):
    logger.info(f"Affected predicates: {affected_predicates}")
    problem = parse_problem(PDDL_PROBLEM_PATH)

    already_booked = defaultdict(list)
    for booked_item in affected_predicates.keys():
        arguments = affected_predicates[booked_item]
        for affected_predicate in arguments:
            parts = affected_predicate.strip("()").split()
            predicate_name = parts[0]
            arguments = parts[1:]
            arg_objects = [Constant(arg) for arg in arguments]
            already_booked[booked_item].append(Predicate(predicate_name, *arg_objects))

    for booked_item in already_booked.keys():
        variables.PREDICATE_PER_ITEM[booked_item] = already_booked[booked_item]

    current_init = set(problem.init)
    for item in already_booked.keys():
        for p in already_booked[item]:
            if p not in current_init:
                current_init.add(p)
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
    variables.PLAN_UPDATED = True
    logger.info(f"PDDL model updated.")

    exit_loop(tool_context)


async def run_predicate_searcher_agent():
    logger.info(f"{'__' * 70}")
    logger.info("Running the predicate searcher agent ...")
    user_input = "Follow the system prompt to complete your assigned tasks. Make sure to execute the tools"
    session_service, runner = await setup_session_and_runner(predicate_tracker)
    await call_agent_async(user_input, runner, session_service)


get_pddl_tool = FunctionTool(func=get_pddl)
get_booked_items_tool = FunctionTool(func=get_booked_items)
update_pddl_model_tool = FunctionTool(func=update_pddl_model)

predicate_tracker = LlmAgent(
    name="predicateTrackerAgent",
    description="You are a predicate tracker agent.",
    instruction="""
            Call 'get_pddl_tool' and 'get_booked_items_tool' tools once each. Do not use the object provided in the context or conversation history, 
            as it may have changed, and the output of the 'get_booked_items_tool' tool is different each time, trust the tool output. If there was an item 
            in the context history but not in the tool output, it means that item has been removed so ignore it.
            
            Then find which predicates in the PDDL model are affected by the booked items, and then execute the 'update_pddl_model_tool' and 
            pass the predicates with their correct parameters to it in the format of {booked_item_A: [affected_predicates], booked_item_B: [affected_predicates],...}.
           
            - Make sure to execute the 'update_pddl_model_tool' tool.
            - DO NOT hallucinate about calling the tools. For real call them.
        """,
    model=local_llm,
    tools=[get_pddl_tool, get_booked_items_tool, update_pddl_model_tool],
    output_key="translation"

)
