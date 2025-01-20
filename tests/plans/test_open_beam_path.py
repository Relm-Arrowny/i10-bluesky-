from collections import defaultdict
from unittest.mock import ANY, Mock, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines.i10 import det_slits, pa_stage, pin_hole, slits
from ophyd_async.testing import get_mock_put

from i10_bluesky.plans import (
    clear_beam_path,
    direct_beam_polan,
    open_dsd_dsu,
    open_s5s6,
    remove_pin_hole,
)

docs = defaultdict(list)


def capture_emitted(name, doc):
    docs[name].append(doc)


async def test_open_s5s6(RE: RunEngine, fake_i10):
    RE(open_s5s6())
    assert await slits().s5.x_gap.user_readback.get_value() > 8
    assert await slits().s5.y_gap.user_readback.get_value() > 8
    assert await slits().s6.x_gap.user_readback.get_value() > 8
    assert await slits().s6.y_gap.user_readback.get_value() > 8


async def test_open_dsd_dsu(RE: RunEngine, fake_i10):
    RE(open_dsd_dsu())
    get_mock_put(det_slits().upstream.user_readback).assert_called_once_with(
        3, wait=ANY
    )
    get_mock_put(det_slits().downstream.user_readback).assert_called_once_with(
        3, wait=ANY
    )
    assert await det_slits().upstream.user_readback.get_value() < 5
    assert await det_slits().downstream.user_readback.get_value() < 5


async def test_remove_pin_hole(RE: RunEngine, fake_i10):
    RE(remove_pin_hole())
    get_mock_put(pin_hole().x.user_readback).assert_called_once_with(69, wait=ANY)
    assert await pin_hole().x.user_readback.get_value() < 70


async def test_direct_beam_polan(RE: RunEngine, fake_i10):
    RE(direct_beam_polan())
    get_mock_put(pa_stage().thp.user_readback).assert_called_once_with(0, wait=ANY)
    get_mock_put(pa_stage().ttp.user_readback).assert_called_once_with(0, wait=ANY)
    get_mock_put(pa_stage().py.user_readback).assert_called_once_with(0, wait=ANY)
    get_mock_put(pa_stage().eta.user_readback).assert_called_once_with(0, wait=ANY)
    assert await pa_stage().thp.user_readback.get_value() == pytest.approx(0, 0.01)
    assert await pa_stage().ttp.user_readback.get_value() == pytest.approx(0, 0.01)
    assert await pa_stage().py.user_readback.get_value() < 1
    assert await pa_stage().eta.user_readback.get_value() == pytest.approx(0, 0.01)


@patch("i10_bluesky.plans.open_beam_path.direct_beam_polan")
@patch("i10_bluesky.plans.open_beam_path.open_dsd_dsu")
@patch("i10_bluesky.plans.open_beam_path.open_s5s6")
@patch("i10_bluesky.plans.open_beam_path.remove_pin_hole")
async def test_clear_beam_path(
    direct_beam_polan: Mock,
    open_dsd_dsu: Mock,
    open_s5s6: Mock,
    remove_pin_hole: Mock,
    RE: RunEngine,
):
    RE(clear_beam_path())
    direct_beam_polan.assert_called_once()
    open_dsd_dsu.assert_called_once()
    open_s5s6.assert_called_once()
    remove_pin_hole.assert_called_once()
