from tools.get_session import get_current_session
from variables import STATE, PDDL_PROBLEM
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_booked_names(current_bookings):
    booked_names = [item[0] for item in current_bookings]
    return booked_names


def get_booked_time(item, current_bookings):
    booked_time = [i[1] for i in current_bookings if i[0] == item]
    return booked_time


def get_booked_items():
    logger.info("_________________________ Getting the booked items...")
    current_session = get_current_session()
    current_bookings = current_session.state.get(STATE, [])

    return current_bookings


def get_obj_type(item):
    obj_type = [obj.type_tag for obj in PDDL_PROBLEM.objects if str(obj.name).lower() == item][0]
    return obj_type
