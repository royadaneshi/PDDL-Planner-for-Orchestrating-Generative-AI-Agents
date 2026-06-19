from google.adk.tools import FunctionTool, ToolContext
import logging
import variables
from variables import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def exit_loop(tool_context: ToolContext):
    logger.info("\n")
    logger.info(f"\n \t \t \t \t{'--- ' * 13} Exit Loop triggered by {tool_context.agent_name} {' ---' * 13}\n")
    tool_context.actions.escalate = True
    tool_context.actions.skip_summarization = True
    session = variables.SESSION_SERVICE.sessions[APP_NAME][USER_ID][SESSION_ID]
    variables.BOOKED_ITEMS = session.state.get(STATE, [])
    logger.info(f"_________________________ Booked Items so far: {variables.BOOKED_ITEMS}")
    return {}


exit_loop_tool = FunctionTool(func=exit_loop)
