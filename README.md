# Multi-Agent Booking System using PDDL planner

This project is a multi-agent orchestration framework designed to handle booking tasks (Hotels, Flights, Taxis) using **PDDL** planner. It utilizes the **Fast Downward** planner to generate optimal sequences of actions while managing budget constraints and plan violations.
A demonstration of the system execution is available in the demo_run_logs file.


### Key Components
* **Orchestration Module:** The brain of the system that manages the workflow.
* **Booking Agent:** An LLM-based agent that books the requested items.
* **Execution Monitoring Module:** Runs after each booking to check for possible agent failures and recover the system if needed.
* **PDDL Planner:** Generates a new plan to recover the system.
---

### Execution
To launch the system, run the launcher.py script from the root directory.
This script serves as the primary entry point: it automatically installs any missing dependencies and then starts the system.

## Language Requirements:
Python 3.13


## Project Structure
```text
.
├── __init__.py
├── agents
│ ├── booking_agent.py
│ └── predicate_searcher_agent.py
├── dataset
│ ├── chicago_hotels.xlsx
│ ├── chicago_taxi.xlsx
│ ├── cost_lookup_table.xlsx
│ └── flights.xlsx
├── demo_run_logs
├── downward
│ ├── ...
├── luncher.py
├── main.py
├── modules
│ ├── call_agent.py
│ ├── execution_monitoring.py
│ └── orchestrator.py
├── pddl_helpers
│ ├── causal_extractor.py
│ ├── pddl_planner.py
│ └── update_pddl_model.py
├── pddl_model
│ ├── OrchestrationPlan.plan
│ ├── domain.pddl
│ └── problem.pddl
├── readme.md
├── run_pddl_planner.py
├── tools
│ ├── exit_tool.py
│ ├── get_booked_items.py
│ ├── get_session.py
│ ├── get_updated_plan.py
│ ├── update_booked_items.py
│ └── update_budget.py
└── variables.py