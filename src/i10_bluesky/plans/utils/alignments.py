from collections.abc import Callable
from enum import Enum

from bluesky import preprocessors as bpp
from bluesky.callbacks.fitting import PeakStats
from bluesky.plan_stubs import abs_set
from bluesky.plans import scan
from dodal.common.types import MsgGenerator
from ophyd_async.core import StandardReadable
from ophyd_async.epics.motor import Motor
from p99_bluesky.plans.fast_scan import fast_scan_1d


class PeakPosition(tuple, Enum):
    COM = ("stats", "com")
    CEN = ("stats", "cen")
    MIN = ("stats", "min")
    MAX = ("stats", "max")
    D_COM = ("derivative_stats", "com")
    D_CEN = ("derivative_stats", "cen")
    D_MIN = ("derivative_stats", "min")
    D_MAX = ("derivative_stats", "max")


def scan_and_move_cen(funcs) -> Callable:
    def inner(**kwargs):
        ps = PeakStats(
            f"{kwargs['motor'].name}",
            f"{kwargs['det'].name}",
            calc_derivative_and_stats=True,
        )
        yield from bpp.subs_wrapper(
            funcs(**kwargs),
            ps,
        )
        print(ps)
        peak_position = get_stat_loc(ps, kwargs["loc"])
        if (
            kwargs["start"] >= peak_position >= kwargs["end"]
            or kwargs["start"] <= peak_position <= kwargs["end"]
        ):
            yield from abs_set(kwargs["motor"], peak_position, wait=True)
        else:
            raise ValueError(f"New position ({peak_position}) is outside scan range.")

    return inner


@scan_and_move_cen
def step_scan_and_move_cen(
    det: StandardReadable,
    motor: Motor,
    start: float,
    end: float,
    num: int,
    loc: PeakPosition = PeakPosition.CEN,
) -> MsgGenerator:
    return scan([det], motor, start, end, num=num)


@scan_and_move_cen
def fast_scan_and_move_cen(
    det: StandardReadable,
    motor: Motor,
    start: float,
    end: float,
    motor_speed: float | None = None,
    loc: PeakPosition = PeakPosition.CEN,
) -> MsgGenerator:
    return fast_scan_1d([det], motor, start, end, motor_speed=motor_speed)


def get_stat_loc(ps: PeakStats, loc: PeakPosition) -> float:
    stat = getattr(ps, loc.value[0])
    stat_pos = getattr(stat, loc.value[1])
    return stat_pos if isinstance(stat_pos, float) else stat_pos[0]
