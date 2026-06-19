import os
from pddl_helpers.pddl_planner import PDDL_Planner

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if "__main__" == __name__:
    pddl_planner = PDDL_Planner()
    pddl_planner.run_fd()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PDDL_PLAN_PATH = os.path.join(BASE_DIR, 'pddl_model', 'OrchestrationPlan.plan')

    with open(PDDL_PLAN_PATH, "r") as f:
        Orchestration_plan = f.read()
    logger.info(f"________________________ Orchestration Plan:\n{Orchestration_plan}\n")
