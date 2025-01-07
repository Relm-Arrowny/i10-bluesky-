from collections import defaultdict
from unittest.mock import Mock

import numpy as np
import pytest
from bluesky.run_engine import RunEngine
from ophyd_async.testing import callback_on_mock_put, set_mock_value
from p99_bluesky.devices.stages import ThreeAxisStage

from i10_bluesky.plans.utils import (
    PeakPosition,
    step_scan_and_move_cen,
)
from i10_bluesky.plans.utils.alignments import fast_scan_and_move_cen
from sim_devices import sim_detector

docs = defaultdict(list)


def capture_emitted(name, doc):
    docs[name].append(doc)


def gaussian(x, mu, sig):
    return (
        1.0
        / (np.sqrt(2.0 * np.pi) * sig)
        * np.exp(-np.power((x - mu) / sig, 2.0) / 2.0)
    )


@pytest.mark.parametrize(
    "test_input, expected_centre",
    [
        (
            [5, -5, 21, 0.1],
            -1,
        ),
        (
            [50, -55, 151, 1],
            21.1,
        ),
        (
            [-1, -2.51241, 31, 0.05],
            -1.2,
        ),
    ],
)
async def test_scan_and_move_cen_success_with_default_value_gaussain(
    RE: RunEngine,
    sim_motor_step: ThreeAxisStage,
    fake_detector: sim_detector,
    test_input,
    expected_centre,
):
    start = test_input[0]
    end = test_input[1]
    num = test_input[2]
    peak_width = test_input[3]
    cen = expected_centre
    # Generate gaussian
    x_data = np.linspace(start, end, num, endpoint=True)
    y_data = gaussian(x_data, cen, peak_width)

    rbv_mocks = Mock()
    y_data = np.append(y_data, [0] * 2)
    y_data = np.array(y_data, dtype=np.float64)
    rbv_mocks.get.side_effect = y_data
    callback_on_mock_put(
        sim_motor_step.x.user_setpoint,
        lambda *_, **__: set_mock_value(fake_detector.value, value=rbv_mocks.get()),
    )

    RE(
        step_scan_and_move_cen(
            det=fake_detector,
            motor=sim_motor_step.x,
            start=start,
            end=end,
            num=num,
        ),
        capture_emitted,
    )
    y_data1 = np.array([])
    x_data1 = np.array([])
    for i in docs["event"]:
        y_data1 = np.append(y_data1, i["data"]["fake_detector-value"])
        x_data1 = np.append(x_data1, i["data"]["sim_motor_step-x-user_readback"])
    assert await sim_motor_step.x.user_setpoint.get_value() == pytest.approx(
        expected_centre, 0.05
    )


@pytest.mark.parametrize(
    "test_input, expected_centre",
    [
        (
            [5, -5, 21, 0.1],
            -1,
        ),
    ],
)
async def test_scan_and_move_cen_success_with_default_value_step(
    RE: RunEngine,
    sim_motor_step: ThreeAxisStage,
    fake_detector: sim_detector,
    test_input,
    expected_centre,
):
    start = test_input[0]
    end = test_input[1]
    num = test_input[2]
    peak_width = test_input[3]
    cen = expected_centre
    # Generate gaussian
    x_data = np.linspace(start, end, num, endpoint=True)
    y_data = gaussian(x_data, cen, peak_width)

    rbv_mocks = Mock()
    y_data = np.append(y_data, [0] * 2)
    y_data = np.array(y_data, dtype=np.float64)
    rbv_mocks.get.side_effect = y_data
    callback_on_mock_put(
        sim_motor_step.x.user_setpoint,
        lambda *_, **__: set_mock_value(fake_detector.value, value=rbv_mocks.get()),
    )

    RE(
        step_scan_and_move_cen(
            det=fake_detector,
            motor=sim_motor_step.x,
            start=start,
            end=end,
            num=num,
        ),
        capture_emitted,
    )
    y_data1 = np.array([])
    x_data1 = np.array([])
    for i in docs["event"]:
        y_data1 = np.append(y_data1, i["data"]["fake_detector-value"])
        x_data1 = np.append(x_data1, i["data"]["sim_motor_step-x-user_readback"])
    assert await sim_motor_step.x.user_setpoint.get_value() == pytest.approx(
        expected_centre, 0.05
    )


async def test_scan_and_move_cen_fail_to_with_wrong_name(
    RE: RunEngine,
    sim_motor_step: ThreeAxisStage,
    fake_detector: sim_detector,
):
    rbv_mocks = Mock()
    y_data = range(0, 19999, 1)
    rbv_mocks.get.side_effect = y_data
    callback_on_mock_put(
        sim_motor_step.x.user_setpoint,
        lambda *_, **__: set_mock_value(fake_detector.value, value=rbv_mocks.get()),
    )
    with pytest.raises(ValueError) as e:
        RE(
            fast_scan_and_move_cen(
                det=fake_detector,
                motor=sim_motor_step.x,
                start=-5,
                end=5,
                motor_speed=100,
                motor_name="wrong_name",
                det_name="-value",
                loc=PeakPosition.CEN,
            ),
            capture_emitted,
        )

    assert str(e.value) == "Fitting failed, check devices name are correct."


@pytest.mark.parametrize(
    "test_input, expected_centre",
    [
        (
            [5, -4, 31, 0.1],
            -5.1,
        ),
    ],
)
async def test_scan_and_move_cen_failed_with_no_peak_in_ranage(
    RE: RunEngine,
    sim_motor_step: ThreeAxisStage,
    fake_detector: sim_detector,
    test_input,
    expected_centre,
):
    start = test_input[0]
    end = test_input[1]
    num = test_input[2]
    peak_width = test_input[3]
    cen = expected_centre
    # Generate gaussian
    x_data = np.linspace(start, end, num, endpoint=True)
    y_data = gaussian(x_data, cen, peak_width)

    rbv_mocks = Mock()
    y_data = np.append(y_data, [0] * 2)
    y_data = np.array(y_data, dtype=np.float64)
    rbv_mocks.get.side_effect = y_data
    callback_on_mock_put(
        sim_motor_step.x.user_setpoint,
        lambda *_, **__: set_mock_value(fake_detector.value, value=rbv_mocks.get()),
    )

    with pytest.raises(ValueError) as e:
        RE(
            step_scan_and_move_cen(
                det=fake_detector,
                motor=sim_motor_step.x,
                start=start,
                end=end,
                num=num,
                motor_name="-user_readback",
                det_name="-value",
                loc=PeakPosition.CEN,
            ),
            capture_emitted,
        )
    assert str(e.value) == "Fitting failed, no peak within scan range."
