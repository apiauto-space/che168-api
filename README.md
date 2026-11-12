# Che168 API clients for Python and JavaScript

Chinese used-car listings from Che168 as clean JSON through the [apiauto.space](https://apiauto.space/en/che168-api/) REST API: search by
make, model, year, price and mileage, fetch one listing by its number, follow new cars and price changes.
No scraper to write or maintain.

| Language | Package | Install | Folder |
|---|---|---|---|
| Python 3.10+ | [`che168-api` on PyPI](https://pypi.org/project/che168-api/) | `pip install che168-api` | [python/](python/) |
| JavaScript / TypeScript | [`che168-api` on npm](https://www.npmjs.com/package/che168-api) | `npm install che168-api` | [js/](js/) |

```python
import che168_api

with che168_api.Client() as client:  # reads APIAUTO_KEY
    for car in client.iter_cars(max_items=20, brand="BYD", year_min=2020):
        print(car["id"], car["title"], car["price"]["amount"])
```

```ts
import { Che168Api } from "che168-api";

for await (const car of new Che168Api().iterCars({ brand: "BYD", year_min: 2020, maxItems: 20 })) {
  console.log(car.id, car.title, car.price.amount);
}
```

Both are thin layers over the general apiauto.space clients ([Python](https://github.com/apiauto-space/apiauto-python),
[JavaScript](https://github.com/apiauto-space/apiauto-js)) with the market preset to `cn`. A key comes
from the Telegram bot [@apiautospace_bot](https://t.me/apiautospace_bot?start=demo); see each package's README.

More: [Che168 API page](https://apiauto.space/en/che168-api/), [API documentation](https://apiauto.space/en/docs/),
[examples in curl, Python, JavaScript and PHP](https://github.com/apiauto-space/che168-api-examples). Clients for
the other sources: [encar-api](https://github.com/apiauto-space/encar-api),
[che168-api](https://github.com/apiauto-space/che168-api), [copart-api](https://github.com/apiauto-space/copart-api),
[iaai-api](https://github.com/apiauto-space/iaai-api).

From the apiauto.space team. Not affiliated with Che168 or Autohome; Che168 is a trademark of its owner and is
named here only to say which listings the clients return. MIT license.
