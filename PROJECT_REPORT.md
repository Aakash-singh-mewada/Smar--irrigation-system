# Project Report: Smart Automatic Irrigation System

**Student:** [Your Name]  **Reg. No:** [Your Reg No]  **Course:** [Course Name]  **Date:** [Month Year]

---

## 1. Abstract
This project presents an automatic irrigation controller that waters crops only when required, using soil moisture, temperature and rain forecast. A Python simulation models soil-water dynamics and compares the controller with a conventional fixed-time schedule. Over 30 simulated weeks, the smart controller used ~41 % less water and kept moisture in the optimal range 98 % of the time. The same logic is provided as an Arduino sketch for real deployment.

## 2. Introduction
Irrigation is the largest consumer of freshwater in agriculture. Timer-based systems ignore actual field conditions, causing over- and under-watering. Automation based on sensor feedback is a practical, low-cost improvement.

## 3. Problem Statement and Objectives
**Problem:** Fixed-schedule or manual irrigation wastes water and does not adapt to weather.
**Objectives:**
1. Build a controller that decides pump ON/OFF from sensor data.
2. Add weather awareness (rain and heat).
3. Add safety mechanisms to protect the pump, crop and system.
4. Quantify the benefit against a fixed timer.
5. Provide a hardware-ready implementation.

## 4. System Design

### 4.1 Architecture
| Block | Role |
|---|---|
| Soil moisture sensor | Measures volumetric water content (%) |
| Temperature / forecast input | Provides weather context |
| Controller | Applies decision rules |
| Relay + pump | Delivers water (2 L/min assumed) |
| Logger | Records data to CSV |

### 4.2 Control Algorithm
- **Validation:** readings outside 0–100 % or missing → pump OFF, reason `SENSOR_FAULT`.
- **While pumping:** stop at ≥ 65 % (`TARGET_REACHED`) or after 20 min (`MAX_RUNTIME`).
- **While idle:** if moisture ≤ threshold (35 %, or 40 % when temp ≥ 35 °C):
  - rain chance ≥ 60 % → `RAIN_EXPECTED` (skip)
  - within 60 min of last stop → `COOLDOWN`
  - else start pump (`SOIL_DRY`).

The gap between 35 % and 65 % is a hysteresis band that prevents rapid switching.

### 4.3 Simulation Model
Per minute: `moisture −= evaporation + drainage`, `+1.5 %` if pump ON, `+0.25 %` if raining.
- Evaporation = 0.006 + 0.0008 × (T − 15) % per minute.
- Temperature follows a daily sine curve (19–35 °C, peak at 15:00).
- Rain: 30 % chance per day, lasting 60–120 min.
- Drainage occurs above 70 % moisture (wasted water).
- Sensor noise: Gaussian, σ = 0.5 %.

These are simplified, assumed parameters, not measured field data.

## 5. Implementation
Python package `irrigation/` with `config.py`, `controller.py`, `simulator.py`, `logger.py`; entry point `main.py`. Nine unit tests cover starting, stopping, rain-skip, heat boost, cooldown, max-runtime and fail-safe. The `hardware/arduino_irrigation.ino` sketch mirrors the logic using an analog moisture sensor and a relay.

## 6. Results

### 6.1 Single run (7 days, seed 42, 3 rain events)
| Metric | Smart | Fixed timer |
|---|---|---|
| Water used | 120 L | 280 L |
| Pump cycles | 3 | 14 |
| Time in 30–70 % | 98.6 % | 83.7 % |
| Moisture range | 35.1–74.8 % | 46.5–86.3 % |

**Water saved: 160 L (57.1 %).**

### 6.2 Average over 30 random weeks (seeds 1–30)
| Metric | Smart | Fixed timer |
|---|---|---|
| Water used per week | 165.3 L | 280.0 L |
| Pump cycles per week | 4.1 | 14.0 |
| Time in optimal band | 98.1 % | 85.0 % |

**Average saving: 41.0 %.** The timer's fixed output does not change with weather, while the smart controller adapts, and the timer pushes moisture above 85 % where excess water drains away.

See `results/moisture_plot.png` for the moisture and pump-state graph.

## 7. Testing
9 unit tests in `tests/test_controller.py`, all passing. Additional validation was done by inspecting decision counts and logs (e.g., `SOIL_OK`, `SOIL_DRY`, `MAX_RUNTIME`).

## 8. Limitations
- Results come from a simplified simulation with assumed parameters; real soil type, crop needs and sensor drift will differ.
- Rain forecast is idealised (no forecast error).
- Single zone, single sensor.
- The Arduino sketch has not been field-tested here and needs sensor calibration.

## 9. Future Scope
Real weather API integration, ESP32 with Wi-Fi/MQTT dashboard and mobile alerts, multi-zone control, crop-specific thresholds, ML-based moisture prediction, solar-powered operation.

## 10. Conclusion
A simple sensor-driven, weather-aware controller can substantially reduce irrigation water use while keeping soil in a healthy range. The modular, tested code and the hardware sketch make it easy to extend into a real prototype.

## 11. How to Reproduce
```bash
python main.py --days 7 --seed 42 --plot
python -m pytest -v
```

## 12. References
1. FAO, *Irrigation Water Management: Irrigation Scheduling* (training manual).
2. Arduino documentation: analog input and relay control (docs.arduino.cc).
3. Python documentation (docs.python.org).
4. Manufacturer datasheet of the capacitive soil moisture sensor used.
