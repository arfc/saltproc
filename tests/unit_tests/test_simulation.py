"""Test Simulation functions"""

def test_check_switch_geo_trigger(simulation):
    """
    This unit test checks that ``check_switch_geo_trigger`` functions
    consistently with its docstring.
    """

    switch_times = [1.0, 3, -31, 86.23333, 1e-16, 2e-18, "two o clock"]
    assert simulation.check_switch_geo_trigger(1.0, switch_times) is True
    assert simulation.check_switch_geo_trigger(3, switch_times) is True
    assert simulation.check_switch_geo_trigger(-32, switch_times) is False
    assert simulation.check_switch_geo_trigger(86.233, switch_times) is False
    assert simulation.check_switch_geo_trigger(1e-16, switch_times) is True
    assert simulation.check_switch_geo_trigger(5e-18, switch_times) is False
    assert simulation.check_switch_geo_trigger("three o clock",
                                               switch_times) is False
    assert simulation.check_switch_geo_trigger("two o clock",
                                               switch_times) is True


def test_read_k_eds_delta(simulation):
    assert simulation.read_k_eds_delta(7) is False
