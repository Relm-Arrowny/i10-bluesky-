from collections.abc import Hashable

from bluesky.plan_stubs import abs_set
from dodal.common.types import MsgGenerator
from ophyd_async.epics.motor import Motor
from pydantic import RootModel


class MotorTable(RootModel):
    root: dict[str, float]


def move_motor_with_look_up(
    slit: Motor,
    size: float,
    motor_table: dict[str, float],
    use_motor_position: bool = False,
    wait=True,
    group: Hashable | None = None,
) -> MsgGenerator:
    MotorTable.model_validate(motor_table)
    if use_motor_position:
        yield from abs_set(slit, size, wait=wait, group=group)  # type: ignore
    elif str(size) in motor_table:
        yield from abs_set(slit, motor_table[str(size)], wait=wait, group=group)  # type: ignore
    else:
        raise ValueError(
            f"No slit with size={size}. Available slit size: {motor_table}"
        )
