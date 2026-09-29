"""Decision logic: the smart controller and a fixed-timer baseline."""
from dataclasses import dataclass
from typing import Optional

from .config import Config


@dataclass
class Decision:
    pump_on: bool
    reason: str


class IrrigationController:
    """Threshold controller with hysteresis, rain-skip, heat boost and safety."""

    def __init__(self, config: Optional[Config] = None):
        self.cfg = config or Config()
        self.pump_on = False
        self._started_at: Optional[int] = None
        self._stopped_at: Optional[int] = None

    def _turn_on(self, t):
        self.pump_on, self._started_at = True, t

    def _turn_off(self, t):
        self.pump_on, self._stopped_at = False, t

    def update(self, t: int, moisture, temp_c: float, rain_prob: float) -> Decision:
        """t = current time in minutes. Returns the pump decision."""
        c = self.cfg

        # Fail-safe: bad sensor reading -> pump OFF
        if moisture is None or not (0.0 <= moisture <= 100.0):
            if self.pump_on:
                self._turn_off(t)
            return Decision(False, "SENSOR_FAULT")

        if self.pump_on:
            if moisture >= c.moisture_high:
                self._turn_off(t)
                return Decision(False, "TARGET_REACHED")
            if t - self._started_at >= c.max_run_minutes:
                self._turn_off(t)
                return Decision(False, "MAX_RUNTIME")
            return Decision(True, "WATERING")

        low = c.moisture_low + (c.hot_temp_boost if temp_c >= c.hot_temp_c else 0.0)
        if moisture > low:
            return Decision(False, "SOIL_OK")
        if rain_prob >= c.rain_skip_prob:
            return Decision(False, "RAIN_EXPECTED")
        if self._stopped_at is not None and t - self._stopped_at < c.min_gap_minutes:
            return Decision(False, "COOLDOWN")
        self._turn_on(t)
        return Decision(True, "SOIL_DRY")


class FixedScheduleController:
    """Baseline: a traditional timer that ignores soil and weather."""

    def __init__(self, config: Optional[Config] = None):
        self.cfg = config or Config()
        self.pump_on = False

    def update(self, t: int, moisture, temp_c: float, rain_prob: float) -> Decision:
        minute = t % 1440
        self.pump_on = any(s <= minute < s + d for s, d in self.cfg.fixed_schedule)
        return Decision(self.pump_on, "TIMER" if self.pump_on else "IDLE")
