"""Virtual field (soil + weather) and the simulation loop."""
import math
import random
from typing import Dict, List, Tuple

from .config import Config


class Environment:
    """Very simple soil-water model driven by temperature, rain and the pump."""

    PUMP_GAIN = 1.5      # % moisture gained per minute of pumping
    RAIN_GAIN = 0.25     # % moisture gained per minute of rain

    def __init__(self, days: int, seed: int = 42, start_moisture: float = 50.0):
        self.rng = random.Random(seed)
        self.moisture = start_moisture
        self.rain_events: List[Tuple[int, int]] = []   # (start_min, end_min)
        for d in range(days):
            if self.rng.random() < 0.30:               # 30% chance of rain per day
                start = d * 1440 + self.rng.randint(0, 1439)
                self.rain_events.append((start, start + self.rng.randint(60, 120)))

    def temperature(self, t: int) -> float:
        hour = (t % 1440) / 60.0
        return 27.0 + 8.0 * math.sin(2 * math.pi * (hour - 9) / 24)  # peak ~15:00

    def is_raining(self, t: int) -> bool:
        return any(s <= t < e for s, e in self.rain_events)

    def rain_forecast(self, t: int) -> float:
        """Chance of rain (%) in the next 3 hours (idealised forecast)."""
        if self.is_raining(t) or any(t < s <= t + 180 for s, _ in self.rain_events):
            return 80.0
        return 10.0

    def read_moisture(self) -> float:
        """Sensor reading = true value + Gaussian noise."""
        return max(0.0, min(100.0, self.moisture + self.rng.gauss(0, 0.5)))

    def advance(self, t: int, dt: int, pump_on: bool) -> None:
        """Advance the soil state by dt minutes."""
        temp = self.temperature(t)
        for i in range(dt):
            evap = 0.006 + 0.0008 * (temp - 15)
            drain = 0.02 * (self.moisture - 70) if self.moisture > 70 else 0.0
            self.moisture -= max(evap, 0.0) + drain
            if pump_on:
                self.moisture += self.PUMP_GAIN
            if self.is_raining(t + i):
                self.moisture += self.RAIN_GAIN
            self.moisture = max(0.0, min(100.0, self.moisture))


def run_simulation(controller, days: int = 7, seed: int = 42,
                   cfg: Config = None) -> Tuple[List[Dict], Dict]:
    """Run one controller for `days` days. Returns (rows, summary)."""
    cfg = cfg or Config()
    env = Environment(days, seed)
    rows: List[Dict] = []
    litres, runs, in_band, prev_on = 0.0, 0, 0, False
    reasons: Dict[str, int] = {}
    steps = days * 1440 // cfg.step_minutes

    for n in range(steps):
        t = n * cfg.step_minutes
        reading = env.read_moisture()
        temp = env.temperature(t)
        dec = controller.update(t, reading, temp, env.rain_forecast(t))
        env.advance(t, cfg.step_minutes, dec.pump_on)

        if dec.pump_on:
            litres += cfg.step_minutes * cfg.flow_lpm
            if not prev_on:
                runs += 1
        prev_on = dec.pump_on
        if cfg.optimal_min <= env.moisture <= cfg.optimal_max:
            in_band += 1
        reasons[dec.reason] = reasons.get(dec.reason, 0) + 1
        rows.append({"minute": t, "day": t // 1440 + 1,
                     "time": f"{(t % 1440)//60:02d}:{(t % 1440)%60:02d}",
                     "moisture": round(env.moisture, 2), "temp_c": round(temp, 1),
                     "raining": int(env.is_raining(t)),
                     "pump_on": int(dec.pump_on), "reason": dec.reason})

    summary = {
        "water_used_litres": round(litres, 1),
        "pump_cycles": runs,
        "time_in_optimal_pct": round(100.0 * in_band / steps, 1),
        "min_moisture": min(r["moisture"] for r in rows),
        "max_moisture": max(r["moisture"] for r in rows),
        "rain_events": len(env.rain_events),
        "decision_counts": reasons,
    }
    return rows, summary
