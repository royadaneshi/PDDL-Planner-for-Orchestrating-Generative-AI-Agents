import variables
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_current_session():
    logger.info("____________________ Get current session")
    return variables.SESSION_SERVICE.sessions[variables.APP_NAME][variables.USER_ID][variables.SESSION_ID]