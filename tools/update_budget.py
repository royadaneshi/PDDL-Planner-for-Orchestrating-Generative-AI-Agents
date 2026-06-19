import logging
import pandas as pd
import variables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_budget(selected_object, current_session, decrease_budget):
    costs = pd.read_excel(variables.COST_LOOKUP_TABLE)
    match = costs.loc[costs['item'].str.lower() == selected_object[0], 'cost'].iloc[0]
    variables.BUDGET = current_session.state.get(variables.BUDGET_KEY, 0)
    initial_budget = variables.BUDGET
    if match:
        booked_cost = int(str(match).replace('$', '').strip())

        if booked_cost > variables.BUDGET:
            return False
        else:
            if decrease_budget:
                variables.BUDGET -= booked_cost
            else:
                variables.BUDGET += booked_cost
            current_session.state[variables.BUDGET_KEY] = variables.BUDGET
            logging.info(
                f"__________________ Item cost:{booked_cost}, Current Budget: {initial_budget} -> Budget updated to: {variables.BUDGET}")
            return True

    return False
