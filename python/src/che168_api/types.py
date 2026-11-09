"""Types of the Che168-only fields of a record.

Every record has the same common keys in every market (see :class:`apiauto.Car`);
the fields only Che168 has are in ``car["raw"]``. :func:`raw` returns them typed::

    from che168_api import raw

    extra = raw(car)
    print(extra.get("source_values"))
"""

from __future__ import annotations

from typing import TypedDict, cast

from apiauto import Car

__all__ = ["Che168Raw", "FxQuote", "raw"]


class FxQuote(TypedDict):
    """The ECB daily rate behind ``price_usd``."""

    currency: str
    usd_per_unit: str
    """Decimal string: US dollars for one unit of ``currency``."""
    date: str
    source: str


class Che168Raw(TypedDict, total=False):
    """Che168-only fields of a record (``car["raw"]``). Keys can be missing; read them with ``.get``."""

    che168_infoid: str
    """The listing number on Che168."""
    dealer_id: str | None
    image_count: int
    drive: str | None
    """``fwd``, ``rwd``, ``awd`` or ``4wd``."""
    power_hp: int | None
    power_kw: int | None
    seats: int | None
    first_registration: str | None
    """First registration date, ``YYYY-MM-DD``."""
    imported: bool | None
    """``True`` for an imported car, ``False`` for one made in China."""
    source_values: dict[str, str | None]
    """Che168's own Chinese spellings of make, model, fuel and transmission."""
    fx: FxQuote | None


def raw(car: Car) -> Che168Raw:
    """The Che168-only fields of a record, typed as :class:`Che168Raw`."""
    return cast(Che168Raw, car.get("raw") or {})
