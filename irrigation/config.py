"""Tunable parameters for the irrigation system."""
from dataclasses import dataclass


@dataclass
class Config:
    # --- Moisture thresholds (% volumetric water content) ---
    moisture_low: float = 35.0      # start watering at/below this
    moisture_high: float = 65.0     # stop watering at/above this
    optimal_min: float = 30.0       # band used only for reporting
    optimal_max: float = 70.0

    # --- Smart rules ---
    hot_temp_c: float = 35.0        # above this, water a bit earlier
    hot_temp_boost: float = 5.0     # raise low threshold by this in heat
    rain_skip_prob: float = 60.0    # skip watering if rain chance >= this (%)

    # --- Safety ---
    max_run_minutes: int = 20       # hard limit per pump cycle
    min_gap_minutes: int = 60       # cool-down between cycles

    # --- Hardware model ---
    flow_lpm: float = 2.0           # pump flow (litres per minute)

    # --- Simulation ---
    step_minutes: int = 5           # controller sampling interval
    # Baseline timer: (start_minute_of_day, duration_minutes)
    fixed_schedule: tuple = ((6 * 60, 10), (18 * 60, 10))
