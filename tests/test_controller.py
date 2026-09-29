from irrigation import Config, IrrigationController, FixedScheduleController


def make():
    return IrrigationController(Config())


def test_starts_when_dry():
    c = make()
    assert c.update(0, 20, 25, 10).pump_on is True


def test_idle_when_soil_ok():
    c = make()
    d = c.update(0, 50, 25, 10)
    assert not d.pump_on and d.reason == "SOIL_OK"


def test_stops_at_target():
    c = make()
    c.update(0, 20, 25, 10)
    d = c.update(5, 66, 25, 10)
    assert not d.pump_on and d.reason == "TARGET_REACHED"


def test_skips_when_rain_expected():
    c = make()
    d = c.update(0, 20, 25, 80)
    assert not d.pump_on and d.reason == "RAIN_EXPECTED"


def test_max_runtime_safety():
    c = make()
    c.update(0, 20, 25, 10)
    d = c.update(20, 40, 25, 10)
    assert not d.pump_on and d.reason == "MAX_RUNTIME"


def test_cooldown_between_cycles():
    c = make()
    c.update(0, 20, 25, 10)
    c.update(20, 40, 25, 10)            # stops at t=20
    d = c.update(30, 20, 25, 10)        # only 10 min later
    assert not d.pump_on and d.reason == "COOLDOWN"
    assert c.update(90, 20, 25, 10).pump_on


def test_heat_raises_threshold():
    c = make()
    assert not c.update(0, 38, 25, 10).pump_on   # 38 > 35 -> ok in mild weather
    assert c.update(5, 38, 38, 10).pump_on       # threshold 40 in heat


def test_sensor_fault_is_failsafe():
    c = make()
    c.update(0, 20, 25, 10)
    d = c.update(5, None, 25, 10)
    assert not d.pump_on and d.reason == "SENSOR_FAULT"
    assert not c.update(10, 150, 25, 10).pump_on


def test_fixed_timer_ignores_soil():
    f = FixedScheduleController(Config())
    assert f.update(6 * 60, 90, 25, 90).pump_on
    assert not f.update(12 * 60, 5, 25, 0).pump_on
