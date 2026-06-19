import os
from collections import defaultdict
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from pddl import parse_domain, parse_problem
from pddl_helpers.causal_extractor import causal_extractor

APP_NAME = "agents"
USER_ID = "12345"
SESSION_ID = "123344"

MAX_ITERATIONS = 2
LLM_MODEL_NAME = "ollama_chat/gemma4:31b"
OLLAMA_BASE_URL = "http://127.0.0.1:11434"

SESSION_SERVICE = InMemorySessionService()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FLIGHT_DATA = os.path.join(BASE_DIR, 'dataset', 'flights.xlsx')
HOTEL_DATA = os.path.join(BASE_DIR, 'dataset', 'chicago_hotels.xlsx')
TAXI_DATA = os.path.join(BASE_DIR, 'dataset', 'chicago_taxi.xlsx')
COST_LOOKUP_TABLE = os.path.join(BASE_DIR, 'dataset', 'cost_lookup_table.xlsx')

PDDL_DOMAIN_PATH = os.path.join(BASE_DIR, 'pddl_model', 'domain.pddl')
PDDL_PROBLEM_PATH = os.path.join(BASE_DIR, 'pddl_model', 'problem.pddl')
TEMP_PDDL_PROBLEM_PATH = os.path.join(BASE_DIR, 'pddl_model', 'temp_problem.pddl')
PDDL_PLAN_PATH = os.path.join(BASE_DIR, 'pddl_model', 'OrchestrationPlan.plan')
FD_PATH = os.path.join(BASE_DIR, 'downward', 'fast-downward.py')

PDDL_DOMAIN = parse_domain(PDDL_DOMAIN_PATH)
PDDL_PROBLEM = parse_problem(PDDL_PROBLEM_PATH)

STATE = "booked_items"
EXECUTION_HISTORY = "execution_history"
EXECUTION_MONITORING_KEY = "state_information"
ORCHESTRATION_RESULT_KEY = "orchestration_result"
ORCHESTRATION_PLAN_KEY = "plan"
CURRENT_OBJECT_TO_BOOK_KEY = "current_item"
BUDGET_KEY = "budget"
VIOLATED = "violated"

# booked items is a list of tuples (booked_item, time)
BOOKED_ITEMS = []
ORCHESTRATION_RESULT = None
TYPE = "Object_type"
OBJECT = "Object"
CURRENT_OBJECT_TO_BOOK = {TYPE: "", OBJECT: ""}
EVERYTHING_OK = "EVERYTHING_OK"
PLAN_CONTRADICTION = "PLAN_CONTRADICTION"
PLAN_UNACHIEVABLE = "PLAN_UNACHIEVABLE"
UPDATED_INIT = None

BUDGET = 215

SUCCESSFUL_BOOKING = [False, ""]
REPLAN_FLAG = False
PREDICATE_PER_ITEM = defaultdict(list)
PLAN_UPDATED = False
CASUAL_LINK = causal_extractor()
with open(PDDL_PLAN_PATH, "r") as f:
    ORCHESTRATION_PLAN = f.read().strip()

local_llm = LiteLlm(
    model=LLM_MODEL_NAME,
    api_base=OLLAMA_BASE_URL,
    api_key="ollama",
    temperature=0.0,
    max_tokens=1000,
)
