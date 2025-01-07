from collections.abc import Callable
from enum import Enum
from typing import TypeVar, cast

from bluesky import preprocessors as bpp
from bluesky.callbacks.fitting import PeakStats
from bluesky.plan_stubs import abs_set
from bluesky.plans import scan
from dodal.common.types import MsgGenerator
from ophyd_async.core import StandardReadable
from ophyd_async.epics.motor import Motor
from p99_bluesky.plans.fast_scan import fast_scan_1d

from i10_bluesky.log import LOGGER


class PeakPosition(tuple, Enum):
    COM = ("stats", "com")
    CEN = ("stats", "cen")
    MIN = ("stats", "min")
    MAX = ("stats", "max")
    D_COM = ("derivative_stats", "com")
    D_CEN = ("derivative_stats", "cen")
    D_MIN = ("derivative_stats", "min")
    D_MAX = ("derivative_stats", "max")


TCallable = TypeVar("TCallable", bound=Callable)


def scan_and_move_cen(funcs: TCallable) -> TCallable:
    def inner(**kwargs):
        if "motor_name" not in kwargs or kwargs["motor_name"] is None:
            kwargs["motor_name"] = "-user_readback"
        if "det_name" not in kwargs or kwargs["det_name"] is None:
            kwargs["det_name"] = "-value"
        if "loc" not in kwargs or kwargs["loc"] is None:
            kwargs["loc"] = PeakPosition.CEN
        ps = PeakStats(
            f"{kwargs['motor'].name}{kwargs['motor_name']}",
            f"{kwargs['det'].name}{kwargs['det_name']}",
            calc_derivative_and_stats=True,
        )
        yield from bpp.subs_wrapper(
            funcs(**kwargs),
            ps,
        )
        peak_position = get_stat_loc(ps, kwargs["loc"])

        LOGGER.info(f"Fit info {ps}")
        yield from abs_set(kwargs["motor"], peak_position, wait=True)

    return cast(TCallable, inner)


@scan_and_move_cen
def step_scan_and_move_cen(
    det: StandardReadable,
    motor: Motor,
    start: float,
    end: float,
    num: int,
    motor_name: str = "-user_readback",
    det_name: str = "-user_readback",
    loc: PeakPosition = PeakPosition.CEN,
) -> MsgGenerator:
    LOGGER.info(
        f"Step scaning {motor}{motor_name} with {det}{det_name} pro-scan move to {loc}"
    )
    return scan([det], motor, start, end, num=num)


@scan_and_move_cen
def fast_scan_and_move_cen(
    det: StandardReadable,
    motor: Motor,
    start: float,
    end: float,
    motor_name: str,
    det_name: str,
    loc: PeakPosition,
    motor_speed: float | None = None,
) -> MsgGenerator:
    LOGGER.info(
        f"Fast scaning {motor}{motor_name} with {det}{det_name} pro-scan move to {loc}"
    )
    return fast_scan_1d([det], motor, start, end, motor_speed=motor_speed)


def get_stat_loc(ps: PeakStats, loc: PeakPosition) -> float:
    stat = getattr(ps, loc.value[0])
    if not stat:
        raise ValueError("Fitting failed, check devices name are correct.")
    elif not stat.fwhm:
        raise ValueError("Fitting failed, no peak within scan range.")

    stat_pos = getattr(stat, loc.value[1])
    return stat_pos if isinstance(stat_pos, float) else stat_pos[0]