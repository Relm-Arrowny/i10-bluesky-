import math

from bluesky.plan_stubs import mv, wait
from dodal.beamlines.i10 import (
    diffractometer,
    rasor_femto_pa_scaler_det,
    simple_stage,
    slits,
)
from dodal.common.types import MsgGenerator
from dodal.devices.slits import Slits
from ophyd_async.core import StandardReadable

from i10_bluesky.plans.utils import PeakPosition, step_scan_and_move_cen


def align_s5s6(
    det: StandardReadable | None = None, det_name: str | None = None
) -> MsgGenerator:
    if det is None:
        det = rasor_femto_pa_scaler_det()
        det_name = "-current"
    diff = diffractometer()
    s_stage = simple_stage()
    slit = slits()
    group_wait = "diff group A"
    yield from mv(diff.tth, 0, diff.th, 0, group=group_wait)  # type: ignore  # See: https://github.com/bluesky/bluesky/issues/1809
    yield from mv(s_stage.y, -3, group=group_wait)  # type: ignore
    yield from wait(group=group_wait)

    yield from align_slit(
        det=det,
        slit=slit.s5,
        x_scan_size=0.1,
        x_final_size=0.65,
        x_range=0.2,
        x_open_size=2,
        x_cen=0,
        y_scan_size=0.1,
        y_final_size=1.3,
        y_open_size=2,
        y_range=2,
        y_cen=0,
        det_name=det_name,
    )


def align_slit(
    det: StandardReadable,
    slit: Slits,
    x_scan_size: float,
    x_final_size: float,
    x_open_size: float,
    y_scan_size: float,
    y_final_size: float,
    y_open_size: float,
    x_range: float,
    x_cen: float,
    y_range: float,
    y_cen: float,
    det_name: str | None = None,
    motor_name: str | None = "",
    centre_type: PeakPosition = PeakPosition.COM,
):
    group_wait = "slits group"
    yield from mv(slit.x_gap, x_scan_size, slit.y_gap, y_open_size, group=group_wait)  # type: ignore
    yield from mv(slit.y_centre, y_cen, group=group_wait)  # type: ignore
    start_pos, end_pos, num = slit_cal_range_num(x_cen, x_range, x_scan_size)
    yield from wait(group=group_wait)
    yield from step_scan_and_move_cen(
        det=det,
        motor=slit.x_centre,
        start=start_pos,
        end=end_pos,
        num=num,
        det_name=det_name,
        motor_name=motor_name,
        loc=centre_type,
    )

    yield from mv(slit.y_gap, y_scan_size, slit.x_gap, x_open_size, group=group_wait)  # type: ignore
    start_pos, end_pos, num = slit_cal_range_num(y_cen, y_range, y_scan_size)
    yield from wait(group=group_wait)
    yield from step_scan_and_move_cen(
        det=det,
        motor=slit.y_centre,
        start=start_pos,
        end=end_pos,
        num=num,
        det_name=det_name,
        loc=centre_type,
    )

    yield from mv(slit.x_gap, x_final_size, slit.y_gap, y_final_size)  # type: ignore


def slit_cal_range_num(cen, range, size) -> tuple[float, float, int]:
    start_pos = cen - range
    end_pos = cen + range
    num = math.ceil(range * 4 / size)
    return start_pos, end_pos, num
