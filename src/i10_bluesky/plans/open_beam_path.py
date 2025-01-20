from collections.abc import Hashable

import bluesky.plan_stubs as bps
from dodal.common.types import MsgGenerator


def open_s5s6(wait: bool = True, group: Hashable | None = None) -> MsgGenerator:
    yield from bps.null()


def open_dsd_dsu(wait: bool = True, group: Hashable | None = None) -> MsgGenerator:
    yield from bps.null()


def remove_pin_hole(wait: bool = True, group: Hashable | None = None) -> MsgGenerator:
    yield from bps.null()


def direct_beam_polan(wait: bool = True, group: Hashable | None = None) -> MsgGenerator:
    yield from bps.null()


def clear_beam_path(wait: bool = True, group: Hashable | None = None) -> MsgGenerator:
    # if group is None:
    #     group = "clear_beam_path"
    # yield from open_s5s6(wait=False, group=group)
    # yield from open_dsd_dsu(wait=False, group=group)
    # yield from remove_pin_hole(wait=False, group=group)
    # yield from direct_beam_polan(wait=False, group=group)
    # if wait:
    #     yield from bps.wait(group=group)
    yield from bps.null()
