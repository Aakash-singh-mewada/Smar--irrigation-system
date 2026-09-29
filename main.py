#!/usr/bin/env python3
"""Smart Automatic Irrigation System - command line entry point.

Examples:
    python main.py
    python main.py --days 14 --seed 7 --plot
"""
import argparse
import os

from irrigation import Config, IrrigationController, FixedScheduleController, run_simulation
from irrigation.logger import write_csv


def plot(smart_rows, fixed_rows, path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping plot (pip install matplotlib)")
        return
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    for ax, rows, title in ((axes[0], smart_rows, "Smart controller"),
                            (axes[1], fixed_rows, "Fixed timer (baseline)")):
        x = [r["minute"] / 1440 for r in rows]
        ax.plot(x, [r["moisture"] for r in rows], label="Soil moisture (%)")
        ax.fill_between(x, 0, 100, where=[r["pump_on"] for r in rows],
                        alpha=0.25, color="tab:blue", label="Pump ON")
        ax.fill_between(x, 0, 100, where=[r["raining"] for r in rows],
                        alpha=0.25, color="tab:gray", label="Rain")
        ax.axhspan(30, 70, alpha=0.08, color="green")
        ax.set_ylim(0, 100); ax.set_ylabel("Moisture %"); ax.set_title(title)
        ax.legend(loc="upper right", fontsize=8)
    axes[1].set_xlabel("Day")
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=130)
    print(f"Plot saved to {path}")


def show(name, s):
    print(f"\n== {name} ==")
    print(f"  Water used        : {s['water_used_litres']} L")
    print(f"  Pump cycles       : {s['pump_cycles']}")
    print(f"  Time in 30-70 %   : {s['time_in_optimal_pct']} %")
    print(f"  Moisture min/max  : {s['min_moisture']} / {s['max_moisture']} %")


def main():
    p = argparse.ArgumentParser(description="Smart Automatic Irrigation System simulator")
    p.add_argument("--days", type=int, default=7, help="days to simulate (default 7)")
    p.add_argument("--seed", type=int, default=42, help="random seed (default 42)")
    p.add_argument("--out", default="results", help="output folder (default results)")
    p.add_argument("--plot", action="store_true", help="save a PNG graph (needs matplotlib)")
    a = p.parse_args()

    cfg = Config()
    smart_rows, smart = run_simulation(IrrigationController(cfg), a.days, a.seed, cfg)
    fixed_rows, fixed = run_simulation(FixedScheduleController(cfg), a.days, a.seed, cfg)

    write_csv(smart_rows, os.path.join(a.out, "smart_log.csv"))
    write_csv(fixed_rows, os.path.join(a.out, "fixed_log.csv"))

    print(f"Simulated {a.days} day(s), seed={a.seed}, rain events={smart['rain_events']}")
    show("Smart controller", smart)
    show("Fixed timer baseline", fixed)
    saved = fixed["water_used_litres"] - smart["water_used_litres"]
    pct = 100 * saved / fixed["water_used_litres"] if fixed["water_used_litres"] else 0
    print(f"\nWater saved by smart controller: {saved:.1f} L ({pct:.1f} %)")
    print("Decision counts (smart):", smart["decision_counts"])
    print(f"Logs written to '{a.out}/'")
    if a.plot:
        plot(smart_rows, fixed_rows, os.path.join(a.out, "moisture_plot.png"))


if __name__ == "__main__":
    main()
