# che168-api — Che168 API client for Python

[![PyPI version](https://img.shields.io/pypi/v/che168-api.svg)](https://pypi.org/project/che168-api/)
[![Python versions](https://img.shields.io/pypi/pyversions/che168-api.svg)](https://pypi.org/project/che168-api/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/apiauto-space/che168-api/blob/main/LICENSE)

`che168-api` gives you Chinese used-car listings from Che168 as clean JSON through the [apiauto.space](https://apiauto.space/en/che168-api/)
REST API, without writing or maintaining a scraper. Search by make, model, year, price and mileage, page
through the whole catalog, fetch one listing by its number and follow a feed of new cars, cars taken off sale
and price changes.

It is a thin layer over the general [`apiauto-space`](https://pypi.org/project/apiauto-space/) client with
the market preset to `cn`, plus types for the Che168-only fields. It comes from the apiauto.space team;
the project is not affiliated with Che168 or Autohome.

- Sync `Client` and `AsyncClient`, retries on 429 and 5xx, one exception class per API error
- `car("59997075")` takes the Che168 listing number as well as the record id
- `Che168Raw` types for the Che168-only fields in `car["raw"]`
- Python 3.10+, `py.typed`, checked with `mypy --strict`

## Install

```bash
pip install che168-api
```

The module you import is `che168_api`.

## Get a key

Open the Telegram bot [@apiautospace_bot](https://t.me/apiautospace_bot?start=demo) and take a free demo
key: one day, 100 data requests, up to 20 cars per request. Paid plans are on the
[pricing page](https://apiauto.space/en/#pricing).

Save the key in the `APIAUTO_KEY` environment variable — the client reads it from there:

```bash
export APIAUTO_KEY="your-key"
```

Keep the key on your server: the API does not accept browser requests.

## Quick start

```python
import che168_api

with che168_api.Client() as client:  # reads APIAUTO_KEY
    page = client.cars(brand="BYD", year_min=2020, limit=20)
    for car in page["items"]:
        print(car["id"], car["title"], car["price"]["amount"], car["price"]["currency"])

    one = client.car("59997075")  # a listing number or "che168:59997075"
    print(one["listing_url"], one["photos"][:1])
```

A record looks like this (shortened; real values from the catalog):

```json
{
  "id": "che168:59997075",
  "market": "cn",
  "source": "che168",
  "source_id": "59997075",
  "title": "2023 Lincoln Navigator",
  "brand": "Lincoln",
  "model": "Navigator",
  "year": 2023,
  "mileage_km": 80000,
  "fuel": "gasoline",
  "transmission": "automatic",
  "body_type": "suv",
  "price": {
    "amount": "136000.00",
    "currency": "CNY"
  },
  "price_usd": "20298.27",
  "location": {
    "country": "CN",
    "region": null,
    "city": "Shenzhen"
  },
  "listing_url": "https://www.che168.com/dealer/534107/59997075.html",
  "is_active": true,
  "first_seen_at": "2026-09-22T16:29:11.202005Z",
  "photos": [
    "https://api.apiauto.space/img/che168:59997075/1.jpg?exp=...&sig=..."
  ],
  "raw": {
    "che168_infoid": "59997075",
    "power_hp": 261,
    "drive": "awd",
    "first_registration": "2023-09-01",
    "imported": false
  }
}
```

Every record has the same keys as in the other apiauto.space markets; a value the source does not provide is
`None`. Prices are decimal strings in CNY, `price_usd` is converted at the ECB daily rate.

## Methods

| Method | What it does | Quota |
|---|---|---|
| `cars(**filters)` | One page of Che168 cars: `brand`, `model`, `year_min`, `year_max`, `price_min`, `price_max`, `mileage_max`, `fuel`, `body_type`, `sort`, `limit`, `cursor` | Cars returned |
| `iter_cars(max_items=None, **filters)` | Every matching car, page after page | Cars returned |
| `car(listing)` | One car by listing number or id, including cars taken off sale in the last 14 days | 1 record |
| `changes(since, type=None)` / `iter_changes(...)` | Feed of `added`, `disappeared`, `price_drop`, `price_up` events | Events returned |
| `brands()` / `models(brand)` | Makes and models with car counts | Free |
| `status()` | Plan access, data age and the number of active cars of the market | Free |
| `usage()` | Your plan, its term and the quota spent | Free |

The general client is at `client.core` for anything else. Errors are the `apiauto` exceptions, re-exported
here: `QuotaExceededError`, `RateLimitError`, `NotFoundError`, `AuthenticationError` and the rest.

## Che168-only fields

```python
from che168_api import raw

extra = raw(car)  # typed as Che168Raw
print(extra.get("source_values"))
```

`Che168Raw` lists the keys with comments; every key is optional, so read them with `.get`.

## Links

- [Che168 API on apiauto.space](https://apiauto.space/en/che168-api/) and the [API documentation](https://apiauto.space/en/docs/)
- [`apiauto-space`](https://pypi.org/project/apiauto-space/): the general client for all markets
- Clients for the other sources: [`encar-api-client`](https://pypi.org/project/encar-api-client/), [`copart-api`](https://pypi.org/project/copart-api/), [`iaai-api`](https://pypi.org/project/iaai-api/)
- [Examples in curl, Python, JavaScript and PHP](https://github.com/apiauto-space/che168-api-examples)
- The JavaScript version of this client: [`che168-api` on npm](https://www.npmjs.com/package/che168-api)

## License

MIT. Che168 is a trademark of its owner; it is named here only to say which listings the client returns.
