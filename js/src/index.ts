/**
 * che168-api — Che168 API client for JavaScript and TypeScript: Chinese used-car listings from Che168 as JSON.
 *
 * A thin layer over the apiauto.space client (`apiauto`) with the market preset to `cn`.
 * From the apiauto.space team. Not affiliated with Che168 or Autohome.
 *
 * @see https://apiauto.space/en/che168-api/
 * @packageDocumentation
 */
import { Apiauto } from "apiauto";
import type {
  ApiautoOptions,
  Car,
  CarsPage,
  CarsParams,
  Change,
  ChangesPage,
  ChangesParams,
  Dictionaries,
  IterOptions,
  MarketStatus,
  ReferenceItem,
  Usage,
} from "apiauto";
import type { Che168Raw } from "./raw.js";

export {
  APIConnectionError,
  Apiauto,
  ApiautoError,
  AuthenticationError,
  BadRequestError,
  NotFoundError,
  PermissionDeniedError,
  QuotaExceededError,
  RateLimitError,
  ServerError,
  ServiceUnavailableError,
} from "apiauto";
export type {
  ApiautoOptions,
  Car,
  CarsPage,
  Change,
  ChangesPage,
  ChangeType,
  Decimal,
  Dictionaries,
  Location,
  MarketStatus,
  Price,
  ReferenceItem,
  ResponseInfo,
  Usage,
} from "apiauto";
export type { Che168Raw, FxQuote } from "./raw.js";
export { VERSION } from "./version.js";

/** The apiauto.space market of Che168. */
export const MARKET = "cn" as const;
/** The `source` of every record this package returns. */
export const SOURCE = "che168" as const;
/** `true` when the market also holds another source and records are filtered on the client. */
export const SHARED_MARKET: boolean = false;

/** Filters of {@link Che168Api.cars}: those of `GET /v1/cars` without `market`. */
export type CarsFilters = Omit<CarsParams, "market">;
/** Parameters of {@link Che168Api.changes}: those of `GET /v1/changes` without `market`. */
export type ChangesFilters = Omit<ChangesParams, "market">;

/**
 * The full record id for a Che168 listing number: `59997075` → `che168:59997075`.
 * An id with the `che168:` prefix is returned as is; another source's prefix throws.
 */
export function carId(listing: string | number): string {
  const text = String(listing).trim();
  if (text === "") throw new TypeError("che168-api: listing must not be empty");
  const sep = text.indexOf(":");
  if (sep === -1) return `${SOURCE}:${text}`;
  if (text.slice(0, sep) !== SOURCE || sep === text.length - 1) {
    throw new TypeError(`che168-api: not a Che168 id: ${JSON.stringify(text)}`);
  }
  return text;
}

/** The Che168-only fields of a record (`car.raw`), typed. */
export function raw(car: Car): Che168Raw {
  return (car.raw ?? {}) as Che168Raw;
}


/**
 * Che168 client of the apiauto.space API. Server-side only: the API does not accept
 * browser requests, and a key in page code is visible to every visitor.
 *
 * @example
 * ```ts
 * import { Che168Api } from "che168-api";
 *
 * const api = new Che168Api(); // reads APIAUTO_KEY
 * for await (const car of api.iterCars({ brand: "BYD", year_min: 2020, maxItems: 20 })) {
 *   console.log(car.id, car.title, car.price.amount);
 * }
 * ```
 */
export class Che168Api {
  /** The general client, for anything this one does not wrap. */
  readonly core: Apiauto;

  /** @param options - The key defaults to the `APIAUTO_KEY` environment variable. */
  constructor(options: ApiautoOptions = {}) {
    this.core = new Apiauto(options);
  }

  /** One page of Che168 cars. Prices are in CNY; every car returned counts against the quota. */
  async cars(filters: CarsFilters = {}): Promise<CarsPage> {
    const page = await this.core.cars({ ...filters, market: MARKET });
    return page;
  }

  /** Every Che168 car matching the filters, page after page; `maxItems` stops early. */
  async *iterCars(filters: CarsFilters & IterOptions = {}): AsyncGenerator<Car, void, undefined> {
    yield* this.core.iterCars({ ...filters, market: MARKET });
  }

  /**
   * One car by listing number (`59997075`) or record id (`che168:59997075`).
   * Cars taken off sale stay available for 14 days with `is_active: false`.
   */
  car(listing: string | number): Promise<Car> {
    return this.core.car(carId(listing));
  }

  /** One page of the change feed: new cars, cars taken off sale and price changes since a moment. */
  async changes(params: ChangesFilters): Promise<ChangesPage> {
    const page = await this.core.changes({ ...params, market: MARKET });
    return page;
  }

  /** Every event of the change feed since a moment, page after page. */
  async *iterChanges(params: ChangesFilters & IterOptions): AsyncGenerator<Change, void, undefined> {
    yield* this.core.iterChanges({ ...params, market: MARKET });
  }

  /** Makes of the cn market with car counts, most frequent first. Free. */
  brands(): Promise<ReferenceItem[]> {
    return this.core.brands(MARKET);
  }

  /** Models of a make with car counts. Free. */
  models(brand: string): Promise<ReferenceItem[]> {
    return this.core.models(MARKET, brand);
  }

  /** Canonical values of `fuel`, `transmission`, `body_type` and more. Free. */
  dictionaries(): Promise<Dictionaries> {
    return this.core.dictionaries();
  }

  /** The cn market: plan access, data age and the number of active cars. Free. */
  async status(): Promise<MarketStatus> {
    const market = (await this.core.markets()).find((item) => item.market === MARKET);
    if (market === undefined) throw new Error(`che168-api: the API did not list the ${MARKET} market`);
    return market;
  }

  /** The plan, its term and how much of the quota is spent. Free. */
  usage(): Promise<Usage> {
    return this.core.usage();
  }
}
