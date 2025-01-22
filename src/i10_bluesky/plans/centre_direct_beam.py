from collections.abc import Hashable

import bluesky.plan_stubs as bps
from dodal.beamlines.i10 import (
    diffractometer,
    simple_stage,
)
from dodal.common.types import MsgGenerator
from ophyd_async.core import StandardReadable

from i10_bluesky.plans.configuration.default_setting import (
    RASOR_DEFAULT_DET,
    RASOR_DEFAULT_DET_NAME_EXTENSION,
)
from i10_bluesky.plans.utils.alignments import PeakPosition, step_scan_and_move_cen


def centre_tth(
    det: StandardReadable = RASOR_DEFAULT_DET,
    det_name: str = RASOR_DEFAULT_DET_NAME_EXTENSION,
    start=-1,
    end=1,
    num=21,
):
    yield from step_scan_and_move_cen(
        det=det,
        motor=diffractometer().tth,
        start=start,
        end=end,
        num=num,
        motor_name=None,
        det_name=det_name,
        loc=PeakPosition.CEN,
    )


def centre_alpha(
    det: StandardReadable = RASOR_DEFAULT_DET,
    det_name: str = RASOR_DEFAULT_DET_NAME_EXTENSION,
    start=-0.8,
    end=0.8,
    num=21,
):
    yield from step_scan_and_move_cen(
        det=det,
        motor=diffractometer().alpha,
        start=start,
        end=end,
        num=num,
        motor_name=None,
        det_name=det_name,
        loc=PeakPosition.CEN,
    )


def centre_det_angles(
    det: StandardReadable = RASOR_DEFAULT_DET,
    det_name: str = RASOR_DEFAULT_DET_NAME_EXTENSION,
):
    yield from centre_tth(det, det_name)
    yield from centre_alpha(det, det_name)


def move_pin_origin(wait: bool = True, group: Hashable | None = None) -> MsgGenerator:
    if wait and group is None:
        group = "move_pin_origin"
    yield from bps.abs_set(simple_stage().x, 0, wait=False, group=group)
    yield from bps.abs_set(simple_stage().y, 0, wait=False, group=group)
    yield from bps.abs_set(simple_stage().z, 0, wait=False, group=group)
    if wait:
        yield from bps.wait(group=group)
