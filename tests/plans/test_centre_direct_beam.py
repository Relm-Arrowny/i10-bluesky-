from collections import defaultdict
from unittest.mock import Mock, call, patch

from bluesky.run_engine import RunEngine
from dodal.beamlines.i10 import diffractometer

from i10_bluesky.plans import centre_alpha, centre_det_angles, centre_tth
from i10_bluesky.plans.configuration.default_setting import (
    RASOR_DEFAULT_DET,
    RASOR_DEFAULT_DET_NAME_EXTENSION,
)
from i10_bluesky.plans.utils.alignments import PeakPosition

docs = defaultdict(list)


def capture_emitted(name, doc):
    docs[name].append(doc)


@patch("i10_bluesky.plans.centre_direct_beam.step_scan_and_move_cen")
async def test_centre_tth(
    fake_step_scan_and_move_cen: Mock,
    RE: RunEngine,
    fake_i10,
):
    RE(centre_tth(), docs)
    fake_step_scan_and_move_cen.assert_called_once_with(
        det=RASOR_DEFAULT_DET,
        motor=diffractometer().tth,
        start=-1,
        end=1,
        num=21,
        motor_name=None,
        det_name=RASOR_DEFAULT_DET_NAME_EXTENSION,
        loc=PeakPosition.CEN,
    )


@patch("i10_bluesky.plans.centre_direct_beam.step_scan_and_move_cen")
async def test_centre_alpha(fake_step_scan_and_move_cen: Mock, RE: RunEngine, fake_i10):
    RE(centre_alpha())

    fake_step_scan_and_move_cen.assert_called_once_with(
        det=RASOR_DEFAULT_DET,
        motor=diffractometer().alpha,
        start=-0.8,
        end=0.8,
        num=21,
        motor_name=None,
        det_name=RASOR_DEFAULT_DET_NAME_EXTENSION,
        loc=PeakPosition.CEN,
    )


@patch("i10_bluesky.plans.centre_direct_beam.step_scan_and_move_cen")
async def test_centre_det_angles(
    fake_step_scan_and_move_cen: Mock,
    RE: RunEngine,
):
    RE(centre_det_angles())
    assert fake_step_scan_and_move_cen.call_args_list[0] == call(
        det=RASOR_DEFAULT_DET,
        motor=diffractometer().tth,
        start=-1,
        end=1,
        num=21,
        motor_name=None,
        det_name=RASOR_DEFAULT_DET_NAME_EXTENSION,
        loc=PeakPosition.CEN,
    )
    assert fake_step_scan_and_move_cen.call_args_list[1] == call(
        det=RASOR_DEFAULT_DET,
        motor=diffractometer().alpha,
        start=-0.8,
        end=0.8,
        num=21,
        motor_name=None,
        det_name=RASOR_DEFAULT_DET_NAME_EXTENSION,
        loc=PeakPosition.CEN,
    )
