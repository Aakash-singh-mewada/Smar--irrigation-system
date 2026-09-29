"""Smart Automatic Irrigation System package."""
from .config import Config
from .controller import IrrigationController, FixedScheduleController, Decision
from .simulator import Environment, run_simulation

__all__ = ["Config", "IrrigationController", "FixedScheduleController",
           "Decision", "Environment", "run_simulation"]
__version__ = "1.0.0"
