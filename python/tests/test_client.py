from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest

import che168_api

KEY = "test-key-1234567890"


def car(car_id: str) -> dict[str, Any]:
    source = car_id.split(":", 1)[0]
    return {"id": car_id, "market": "cn", "source": source, "title": "car", "price": {"amount": "1.00"}}


def page(ids: list[str], next_cursor: str | None = None, count: int | None = None) -> dict[str, Any]:
    return {"items": [car(i) for i in ids], "next_cursor": next_cursor, "count": count}


class Recorder:
    """Replays queued JSON bodies and records the requests."""

    def __init__(self, *bodies: Any) -> None:
        self.bodies = list(bodies)
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(200, json=self.bodies.pop(0))

    def params(self, index: int = -1) -> dict[str, str]:
        return dict(self.requests[index].url.params)


def client(recorder: Callable[[httpx.Request], httpx.Response]) -> che168_api.Client:
    http = httpx.Client(transport=httpx.MockTransport(recorder))
    return che168_api.Client(KEY, http_client=http, max_retries=0)


def test_constants() -> None:
    assert che168_api.MARKET == "cn"
    assert che168_api.SOURCE == "che168"
    assert che168_api.SHARED_MARKET is False
    assert che168_api.__version__ == "0.1.0"


def test_cars_presets_the_market() -> None:
    rec = Recorder(page(["che168:1", "che168:2"], count=2))
    with client(rec) as api:
        result = api.cars(brand="BYD", year_min=2020, limit=2)
    assert [c["id"] for c in result["items"]] == ["che168:1", "che168:2"]
    assert rec.requests[0].url.path == "/v1/cars"
    assert rec.params() == {"market": "cn", "brand": "BYD", "year_min": "2020", "limit": "2"}
    assert rec.requests[0].headers["x-api-key"] == KEY


def test_unknown_filter_is_rejected() -> None:
    with client(Recorder()) as api, pytest.raises(TypeError):
        api.cars(market="kr")  # type: ignore[call-arg]


@pytest.mark.parametrize(
    ("listing", "path"),
    [
        ("59997075", "/v1/cars/che168:59997075"),
        (59997075, "/v1/cars/che168:59997075"),
        ("che168:59997075", "/v1/cars/che168:59997075"),
    ],
)
def test_car_accepts_number_or_id(listing: str | int, path: str) -> None:
    rec = Recorder(car("che168:59997075"))
    with client(rec) as api:
        assert api.car(listing)["id"] == "che168:59997075"
    assert rec.requests[0].url.path == path


@pytest.mark.parametrize("bad", ["", "  ", "other:123", "che168:"])
def test_car_id_rejects_foreign_ids(bad: str) -> None:
    with pytest.raises(ValueError, match=r"\S"):
        che168_api.car_id(bad)


def test_brands_models_and_status() -> None:
    markets = {
        "items": [
            {"market": "kr", "source": "encar", "active_cars": 1},
            {"market": "cn", "source": "che168", "active_cars": 2},
            {"market": "us", "source": "copart+iaai", "active_cars": 3},
        ]
    }
    rec = Recorder([{"name": "BYD", "count": 5}], [{"name": "Han", "count": 2}], markets)
    with client(rec) as api:
        assert api.brands()[0]["name"] == "BYD"
        assert rec.params(0) == {"market": "cn"}
        assert api.models("BYD")[0]["count"] == 2
        assert rec.params(1) == {"market": "cn", "brand": "BYD"}
        assert api.status()["market"] == "cn"


def test_raw_is_typed_view() -> None:
    record: Any = {"id": "che168:59997075", "raw": {"source_values": {"brand": "x"}}}
    assert che168_api.raw(record).get("source_values") == {"brand": "x"}
    assert che168_api.raw({"id": "che168:59997075"}) == {}  # type: ignore[typeddict-item]


def test_iter_cars_passes_max_items_to_the_last_page() -> None:
    rec = Recorder(page(["che168:1", "che168:2"], next_cursor="c2"), page(["che168:3"]))
    with client(rec) as api:
        ids = [c["id"] for c in api.iter_cars(max_items=3, limit=2)]
    assert ids == ["che168:1", "che168:2", "che168:3"]
    assert rec.params(1)["cursor"] == "c2"
    assert rec.params(1)["limit"] == "1"


def test_changes_presets_the_market() -> None:
    rec = Recorder({"items": [{"id": 1, "car_id": "che168:1", "type": "added"}], "next_cursor": None})
    with client(rec) as api:
        result = api.changes("2026-11-01T00:00:00Z", type=["added", "price_drop"])
    assert result["items"][0]["car_id"] == "che168:1"
    assert rec.requests[0].url.params.get_list("type") == ["added", "price_drop"]
    assert rec.params()["market"] == "cn"


def test_async_client() -> None:
    rec = Recorder(page(["che168:1"]), car("che168:59997075"), page(["che168:1"]))

    async def run() -> list[str]:
        http = httpx.AsyncClient(transport=httpx.MockTransport(rec))
        async with che168_api.AsyncClient(KEY, http_client=http, max_retries=0) as api:
            first = await api.cars(limit=1)
            one = await api.car("59997075")
            more = [c["id"] async for c in api.iter_cars(max_items=1, limit=1)]
        await http.aclose()
        return [first["items"][0]["id"], one["id"], *more]

    assert asyncio.run(run()) == ["che168:1", "che168:59997075", "che168:1"]
    assert all(r.url.params.get("market") in (None, "cn") for r in rec.requests)


def test_errors_are_the_apiauto_ones() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = {"error": {"code": "not_found", "message": "no such car"}}
        return httpx.Response(404, content=json.dumps(body), headers={"content-type": "application/json"})

    with client(handler) as api, pytest.raises(che168_api.NotFoundError):
        api.car("1")
