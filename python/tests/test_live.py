"""Smoke test against the live API; runs only when APIAUTO_KEY is set and spends a few records."""

from __future__ import annotations

import os

import pytest

import che168_api

pytestmark = pytest.mark.skipif(not os.environ.get("APIAUTO_KEY"), reason="set APIAUTO_KEY to run")


def test_live_cars_and_car() -> None:
    with che168_api.Client() as api:
        assert api.status()["market"] == "cn"
        cars = list(api.iter_cars(max_items=3, limit=3))
        assert cars, "the catalog returned no Che168 cars"
        assert all(car["source"] == "che168" for car in cars)
        one = api.car(cars[0]["source_id"])
        assert one["id"] == cars[0]["id"]
        assert isinstance(che168_api.raw(one), dict)
