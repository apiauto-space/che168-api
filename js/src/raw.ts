// Types of the Che168-only fields of a record (`car.raw`).
/** The ECB daily rate behind `price_usd`. */
export interface FxQuote {
  currency: string;
  /** Decimal string: US dollars for one unit of `currency`. */
  usd_per_unit: string;
  date: string;
  source: string;
}

/** Che168-only fields of a record (`car.raw`). Every key is optional. */
export interface Che168Raw {
  /** The listing number on Che168. */
  che168_infoid?: string;
  dealer_id?: string | null;
  image_count?: number;
  /** `fwd`, `rwd`, `awd` or `4wd`. */
  drive?: string | null;
  power_hp?: number | null;
  power_kw?: number | null;
  seats?: number | null;
  /** First registration date, `YYYY-MM-DD`. */
  first_registration?: string | null;
  /** `true` for an imported car, `false` for one made in China. */
  imported?: boolean | null;
  /** Che168's own Chinese spellings of make, model, fuel and transmission. */
  source_values?: Record<string, string | null>;
  fx?: FxQuote | null;
}
