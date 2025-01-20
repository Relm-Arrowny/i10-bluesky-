from collections import defaultdict
from unittest.mock import ANY, Mock, patch

from bluesky.run_engine import RunEngine
from bluesky.simulators import RunEngineSimulator
from dodal.beamlines.i10 import diffractometer

from i10_bluesky.plans import centre_alpha, centre_det_angles, centre_tth

from ..helper_functions import check_msg_set, check_mv_wait

docs = defaultdict(list)


def capture_emitted(name, doc):
    docs[name].append(doc)


@patch("i10_bluesky.plans.utils.step_scan_and_move_cen")
async def test_centre_tth(
    fake_step_scan_and_move_cen: Mock, RE: RunEngine, fake_i10, fake_detector
):
    sim = RunEngineSimulator()
    msgs = sim.simulate_plan(centre_tth(det=fake_detector))
    msgs = check_msg_set(msgs=msgs, obj=diffractometer().tth, value=0)
    msgs = check_mv_wait(msgs=msgs, wait_group=ANY)
    fake_step_scan_and_move_cen.assert_called_once_with(
        det=fake_detector, motor=diffractometer().tth, start=-1.0, end=1.0, num=21
    )


@patch("i10_bluesky.plans.utils.step_scan_and_move_cen")
async def test_centre_alpha(
    fake_step_scan_and_move_cen: Mock, RE: RunEngine, fake_i10, fake_detector
):
    sim = RunEngineSimulator()
    msgs = sim.simulate_plan(centre_alpha(det=fake_detector))
    msgs = check_msg_set(msgs=msgs, obj=diffractometer().alpha, value=0)
    msgs = check_mv_wait(msgs=msgs, wait_group=ANY)
    fake_step_scan_and_move_cen.assert_called_once_with(
        det=fake_detector, motor=diffractometer().alpha, start=-0.8, end=0.8, num=21
    )


@patch("i10_bluesky.plans.centre_tth,")
@patch("i10_bluesky.plans.centre_alpha")
async def test_centre_det_angles(
    centre_tth: Mock, centre_alpha: Mock, RE: RunEngine, fake_detector
):
    RE(centre_det_angles(det=fake_detector))
    centre_tth.assert_called_once()
    centre_alpha.assert_called_once()
