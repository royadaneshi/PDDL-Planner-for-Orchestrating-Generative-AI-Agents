import pandas as pd
from google.adk.agents import LlmAgent

import variables
from tools.get_booked_items import get_booked_names
from tools.get_session import get_current_session
from tools.update_budget import update_budget
from variables import *
from google.adk.tools import FunctionTool, ToolContext
from tools.exit_tool import exit_loop
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_violated_history():
    current_session = get_current_session()
    previous_violated_items = current_session.state.get(VIOLATED, [])
    return f"These items should not be booked again: {previous_violated_items}."


def get_object_to_book():
    """
    This function returns the current object name and its object type
    """
    logger.info("\n")
    logger.info(f"Getting object to book...")
    logger.info(f"{'__' * 70}")

    current_session = get_current_session()
    booking_object = current_session.state.get(CURRENT_OBJECT_TO_BOOK_KEY, {TYPE: "", OBJECT: ""})
    variables.CURRENT_OBJECT_TO_BOOK = booking_object
    return_summary = f"Current object to book: {variables.CURRENT_OBJECT_TO_BOOK}"
    logger.info(f"{return_summary}.\n")
    return return_summary


def book_object(tool_context: ToolContext, selected_object: str, selected_object_time: str):
    logger.info("\n")
    logger.info(f"Booking object {selected_object} ...")
    logger.info(f"{'__' * 70}")

    current_session = get_current_session()
    selected_object = str(selected_object).lower()
    current_bookings = current_session.state.get(STATE, [])

    if selected_object in get_booked_names(current_bookings):
        return f"Item {selected_object} has already booked."

    booking_entry = f"Booked object: {selected_object}"
    enough_budget = update_budget((selected_object, selected_object_time), current_session, True)

    current_session = get_current_session()
    previous_violated_items = current_session.state.get(VIOLATED, [])

    if selected_object in get_booked_names(previous_violated_items):
        return f"Item {selected_object} has already been booked and rolled back because it is unachievable. Select another item."
    if enough_budget:
        current_bookings.append((selected_object, selected_object_time))
        current_session.state[STATE] = current_bookings
        logger.info(f"__________________ {booking_entry}\n")
        SUCCESSFUL_BOOKING[0] = True
        SUCCESSFUL_BOOKING[1] = booking_entry
        exit_loop(tool_context)
        return f"{booking_entry}. STATUS: SUCCESS. TERMINATE_LOOP_NOW."
    else:
        Booking_summary = f"Can't book {selected_object}, because lack of budget."
        SUCCESSFUL_BOOKING[0] = False
        SUCCESSFUL_BOOKING[1] = Booking_summary
        logger.info(f"{Booking_summary}.\n")
        replan(tool_context)
        return f"Can't book {selected_object}, because lack of budget."


def get_causal_link():
    """this function gets the causal link and send it to the agent so it decides which
    object to keep and select"""
    logger.info("\n")
    logger.info(f"Getting causal link...")
    logger.info(f"{'__' * 70}")
    links = variables.CASUAL_LINK
    return f"Causal Link: {str(links)}"


def get_available_objects():
    logger.info("\n")
    logger.info(f"Getting available objects...")
    taxis = pd.read_excel(variables.TAXI_DATA)
    hotels = pd.read_excel(variables.HOTEL_DATA)
    flights = pd.read_excel(variables.FLIGHT_DATA)
    return f"These are the available taxis:{taxis}, hotels:{hotels}, and flights:{flights}"


def get_budget():
    logger.info("\n")
    logger.info(f"Getting budget...")
    current_session = get_current_session()
    if BUDGET_KEY not in current_session.state:
        current_session.state[BUDGET_KEY] = variables.BUDGET

    current_budget = current_session.state[BUDGET_KEY]
    budget = f"Current budget: {str(current_budget)}"
    logger.info(f"_____________________ {budget}")
    return budget


async def replan(tool_context: ToolContext):
    """
    Because of the lack of budget the agent couldn't book any item from the current object type.
    So, in this function, we go one step back, remove the last booked item, and replan from there.
    The full implementation of this kind of failure remains a direction for future work.
    """
    Booking_summary = "Can't book the requested object, due to insufficient budget."
    variables.REPLAN_FLAG = True
    SUCCESSFUL_BOOKING[0] = False
    SUCCESSFUL_BOOKING[1] = Booking_summary
    logger.info(f"{Booking_summary} Exit booking agent...")
    # exit this turn of booking agent bc it may continue working with previous data and doesn't start from the first step
    exit_loop(tool_context)


get_object_to_book_tool = FunctionTool(func=get_object_to_book)
get_causal_link_tool = FunctionTool(func=get_causal_link)
book_object_tool = FunctionTool(func=book_object)
get_available_objects_tool = FunctionTool(func=get_available_objects)
get_budget_tool = FunctionTool(func=get_budget)
replan_tool = FunctionTool(func=replan)
get_violated_history_tool = FunctionTool(func=get_violated_history)

selection_booking = LlmAgent(
    name="selectAndBookObject",
    description="You are an object booking agent.",
    instruction=f"""
            First, get the object to book and its object type from the 'get_object_to_book_tool' tool. Do not use the object provided in the context or conversation history, as it may have changed, and the output of the 'get_object_to_book_tool' tool is different each time.
            TASK:
            1. Call 'get_causal_link_tool' tool to get the causal link.
            2. Call 'get_available_objects_tool' tool to get the available objects and their information.
            3. Call 'get_budget_tool' tool to get the current available budget.
            4. Call the 'get_violated_history_tool' to retrieve items that were previously booked but did not work. Make sure not to select any item from this list.
            5. Based on the causal link information, the current budget, 'get_violated_history_tool' results, and the type of the current object to book, select an object to book. If you can’t book the exact item in the casual link, look for alternative items of the same type to book.
            5-1. If no object of the desired type can be booked, IMMEDIATELY call 'replan_tool', your task is finished.
            5-2. If there is an object that can be booked (if there is more than one possible item, select the one that is cheaper and is not in 'get_violated_history_tool' output. DO NOT consider timing.), immediately call book_object_tool with the selected object. Your task is then complete.    
           
            STRICT RULES:
            - Do not summarize objects.
            - Don't provide extra explanations.
            - Once you decided which object to book, your turn is over, you have only to call 'book_object_tool'.
            - Don't look at conversation history as it may not be complete, only decide act based on the tools outputs.
            - Booking an object is more important than strictly following the plan.
        """,
    tools=[get_object_to_book_tool, get_causal_link_tool, get_available_objects_tool, get_budget_tool,
           get_violated_history_tool, book_object_tool,
           replan_tool],
    model=local_llm,
    output_key="booked_object"

)
