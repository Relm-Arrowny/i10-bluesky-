import math

from bluesky.plan_stubs import abs_set, mv, wait
from dodal.beamlines.i10 import (
    diffractometer,
    rasor_femto_pa_scaler_det,
    simple_stage,
    slits,
)
from dodal.common.types import MsgGenerator
from dodal.devices.slits import Slits
from ophyd_async.core import StandardReadable

from i10_bluesky.log import LOGGER
from i10_bluesky.plans.utils import PeakPosition, step_scan_and_move_cen


def align_s5s6(
    det: StandardReadable | None = None, det_name: str | None = None
) -> MsgGenerator:
    """
    Plan to align the s5s6 slits with the straight through beam
    and RASOR detector, it define where all the motor should be and call
    align slits

    Parameters
    ----------
    det: (Optional)
        Detector that use for the alignments, default is rasor photodiode.
    det_name: (Optional)
        Name of the detector for fitting only requires.
    """

    if det is None:
        det = rasor_femto_pa_scaler_det()
        det_name = "-current"
    diff = diffractometer()
    s_stage = simple_stage()
    slit = slits()
    group_wait = "diff group A"
    LOGGER.info("Moving to straight through and dropping sample")
    yield from abs_set(diff.tth, 0, group=group_wait)
    yield from abs_set(diff.th, 0, group=group_wait)  # type: ignore  # See: https://github.com/bluesky/bluesky/issues/1809
    yield from abs_set(s_stage.y, -3, group=group_wait)  # type: ignore
    yield from wait(group=group_wait)
    LOGGER.info("Aligning s5")
    yield from align_slit(
        det=det,
        slit=slit.s5,
        x_scan_size=0.1,
        x_final_size=0.65,
        x_range=2,
        x_open_size=4,
        x_cen=0,
        y_scan_size=0.1,
        y_final_size=1.3,
        y_open_size=4,
        y_range=2,
        y_cen=0,
        det_name=det_name,
    )
    LOGGER.info("Aligning s6")
    yield from align_slit(
        det=det,
        slit=slit.s6,
        x_scan_size=0.1,
        x_final_size=0.45,
        x_range=2,
        x_open_size=4,
        x_cen=0,
        y_scan_size=0.1,
        y_final_size=0.6,
        y_open_size=4,
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
    """
    Plan to align a pair of standard x-y slits,
    it does a pair of slits scan and go to the centre of mass by default.

    Parameters
    ----------
    det: StandardReadable
        Detector to be use for alignment.
    slit: Slits,
        x-y slits.
    x_scan_size: float,
        The size of the x slit use for alignment.
    x_final_size: float,
        The size of the x slit to set to after alignment.
    x_open_size: float,
        The size of the x slit during y slit alignment.
    y_scan_size: float,
        The size of the y slit use for alignment.
    y_final_size: float,
        The size of the y slit to set to after alignment.
    y_open_size: float,
        The size of the y slit during x slit alignment.
    x_range: float,
        The x slit range, range is the distant from the centre.
        e.g. a range of 1 with centre at 0 will cover -1 to 1.
    x_cen: float,
        The best guess of x slit centre.
    y_range: float,
        The y slit range.
    y_cen: float,
        The best guess of y slit centre.
    det_name: str | None = None,
        det_name is optional, it is used for indicate which signal to fit
        when there are multiple HINTED_SIGNAL/non standard name.
        It only add to the last part of the detector name if/when required.
    motor_name: str | None = "",
        The name of the motor, same as det_name.
    centre_type: PeakPosition = PeakPosition.COM
        Where to move the slits, it goes to centre of mass by default.
        see PeakPosition for other options.
    """
    group_wait = "slits group"
    yield from abs_set(slit.x_gap, x_scan_size, group=group_wait)
    yield from abs_set(slit.y_gap, y_open_size, group=group_wait)
    LOGGER.info(f"Moving to starting position for {slit.x_centre.name} alignment.")
    yield from wait(group=group_wait)
    yield from mv(slit.y_centre, y_cen, group=group_wait)  # type: ignore
    start_pos, end_pos, num = slit_cal_range_num(x_cen, x_range, x_scan_size)

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

    yield from abs_set(slit.y_gap, y_scan_size, group=group_wait)
    yield from abs_set(slit.x_gap, x_open_size, group=group_wait)
    LOGGER.info(f"Moving to starting position for {slit.y_centre.name} alignment.")
    yield from wait(group=group_wait)
    start_pos, end_pos, num = slit_cal_range_num(y_cen, y_range, y_scan_size)

    yield from step_scan_and_move_cen(
        det=det,
        motor=slit.y_centre,
        start=start_pos,
        end=end_pos,
        num=num,
        det_name=det_name,
        loc=centre_type,
    )
    yield from abs_set(slit.x_gap, x_final_size, group=group_wait)
    yield from abs_set(slit.y_gap, y_final_size, group=group_wait)
    yield from wait(group=group_wait)


def slit_cal_range_num(cen, range, size) -> tuple[float, float, int]:
    """Calculate the start, end and the number of step for the scan"""
    start_pos = cen - range
    end_pos = cen + range
    num = math.ceil(abs(range * 4.0 / size))
    return start_pos, end_pos, num
