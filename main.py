"""
In this  function we start the system
"""
import asyncio
import logging
from dotenv import load_dotenv
from modules.orchestrator import orchestration

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()

if __name__ == "__main__":
    # Caution! At each run the problem.pddl should be updated to its initial version, because it being changed during the execution
    asyncio.run(orchestration())
