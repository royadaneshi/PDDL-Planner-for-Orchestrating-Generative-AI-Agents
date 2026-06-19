import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDDL_Planner:
    def __init__(self):
        self.DOMAIN_FILE = os.path.join('pddl_model', 'domain.pddl')
        self.PROBLEM_FILE = os.path.join('pddl_model', 'problem.pddl')
        self.FD_PATH = os.path.join('downward', 'fast-downward.py')
        self.PDDL_PLAN_PATH = os.path.join('pddl_model', 'OrchestrationPlan.plan')

    def set_problem_path(self, new_path):
        self.PROBLEM_FILE = new_path

    def run_fd(self):
        cmd = [
            "python3", self.FD_PATH,
            "--plan-file", self.PDDL_PLAN_PATH,
            self.DOMAIN_FILE,
            self.PROBLEM_FILE,
            "--search", "lazy_greedy([ff()], preferred=[ff()])"
        ]

        logger.info(f" Running PDDL Planner...")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if "Solution found." in result.stdout:
                logger.info(" Plan found!")

                with open(self.PDDL_PLAN_PATH) as f:
                    lines = [l for l in f if not l.startswith(";")]
                if len(lines) > 0:
                    lines[-1] = lines[-1].strip()
                with open(self.PDDL_PLAN_PATH, "w") as f:
                    f.writelines(lines)
                return True
            else:
                logger.info(" Planner finished but no solution was found.")
                return False

        except subprocess.CalledProcessError as e:
            logger.info(" Planner failed to execute.No other possible plan could be found.")
            logger.info(" --- Error Detail ---")
            print(e.stderr if e.stderr else e.stdout)
            return False
