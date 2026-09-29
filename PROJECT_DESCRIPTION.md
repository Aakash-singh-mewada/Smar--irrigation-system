# Project Description

**Title:** Smart Automatic Irrigation System
**Domain:** Agriculture Automation / Embedded & Control Systems / Sustainability
**Language:** Python 3 (with an Arduino C++ reference implementation)

## Problem Statement
Traditional irrigation runs on fixed timers or manual effort. Fields get watered even after rain or when the soil is already wet, which wastes water and energy and can damage crops through over-watering. Farmers also lose time monitoring fields by hand. Agriculture accounts for the majority of freshwater use in India, so even small efficiency gains matter.

## Objective
Design a system that automatically irrigates only when needed by reading soil moisture, temperature and rain forecast, while protecting the pump and crops with safety rules.

## Solution Overview
The project implements a rule-based controller with hysteresis:

1. Read soil moisture (with sensor-fault validation).
2. If moisture ≤ 35 % (or ≤ 40 % in heat ≥ 35 °C), consider watering.
3. Skip if rain is likely (≥ 60 %) or the pump is in its cool-down period.
4. Stop when moisture reaches 65 %, or after 20 minutes, whichever comes first.

A simulated field (soil evaporation, drainage, daily temperature cycle, random rain) lets the controller be tested with no hardware. A fixed-timer baseline is run on identical weather for comparison.

## Key Features
- Moisture-based automatic pump control with hysteresis
- Rain and heat awareness
- Safety limits and sensor fail-safe
- CSV logging, graphs and a water-saving report
- Unit-tested logic and an Arduino hardware sketch

## Technologies
Python 3 (standard library), matplotlib (optional), pytest, Git/GitHub, Arduino C++.

## Outcome
Across 30 simulated weeks, the smart controller used about **41 % less water** than a fixed timer (165 L vs 280 L per week) and kept soil moisture in the optimal 30–70 % range **98 %** of the time (timer: 85 %).

## Learning Outcomes
Control-logic design, simulation modelling, modular Python, unit testing, data logging, version control, and sustainable-engineering thinking.
