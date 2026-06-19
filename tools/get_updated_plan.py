from google.adk.tools import FunctionTool
import variables


def get_plan():
    with open(variables.PDDL_PLAN_PATH, "r") as f:
        variables.ORCHESTRATION_PLAN = f.read()
    return f"This is the updated plan: {variables.ORCHESTRATION_PLAN}."


get_plan_tool = FunctionTool(func=get_plan)
