import countriesRaw        from '~/utils/generated/countries.json'
import categoriesRaw       from '~/utils/generated/categories.json'
import yearsRaw            from '~/utils/generated/years.json'
import tradeConnectionsRaw from '~/utils/generated/tradeconnections.json'

// ─── Types ────────────────────────────────────────────────────────────────

export interface CategoryTrade {
  imports: { usd: number; weight: number }
  exports: { usd: number; weight: number }
}

export interface YearlyPoint {
  year: number
  imports: { usd: number; weight: number }
  exports: { usd: number; weight: number }
}

export interface CountryTrade {
  iso3: string
  name: string
  lat: number
  lng: number
  imports: { usd: number; weight: number }
  exports: { usd: number; weight: number }
  byCategory: Partial<Record<string, CategoryTrade>>
  series: YearlyPoint[]
}

export interface TradeConnectionYear {
  top3exportCountries: Record<string, number>
  top3importers: Record<string, number>
}

export interface TradeFlow {
  fromIso3: string; fromLat: number; fromLng: number
  toIso3: string;   toLat: number;   toLng: number
  usd: number; weight: number; type: 'export' | 'import'
}

export interface SearchItem {
  type: 'country' | 'category' | 'year'
  label: string
  path: string
}

// ─── Data from generated JSON ─────────────────────────────────────────────

export const TRADE_DATA: CountryTrade[] = countriesRaw as unknown as CountryTrade[]

export const TRADE_CONNECTIONS: Record<string, Record<string, TradeConnectionYear>> =
  tradeConnectionsRaw as unknown as Record<string, Record<string, TradeConnectionYear>>

// Display names for ISO3 codes not present in TRADE_DATA
const SPECIAL_ISO3_NAMES: Record<string, string> = {
  WLD: 'World',
  EUU: 'European Union',
}

export function iso3ToName(iso3: string): string {
  return SPECIAL_ISO3_NAMES[iso3]
    ?? TRADE_DATA.find(c => c.iso3.toUpperCase() === iso3.toUpperCase())?.name
    ?? iso3
}

export const CATEGORIES: string[] = [
  ...new Set((categoriesRaw as Array<{ name: string }>).map(c => c.name))
]

export const YEARS: number[] = (yearsRaw as Array<{ year: number }>).map(y => y.year)

// ─── Helper functions ──────────────────────────────────────────────────────

export function getTradeConnections(iso3: string, year: string): TradeConnectionYear | null {
  return TRADE_CONNECTIONS[iso3.toUpperCase()]?.[year] ?? null
}

export function getCountry(iso3: string): CountryTrade | undefined {
  return TRADE_DATA.find(c => c.iso3.toUpperCase() === iso3.toUpperCase())
}

export function getTradeValue(
  country: CountryTrade,
  type: 'imports' | 'exports',
  metric: 'usd' | 'weight',
  category: string | null,
): number {
  if (category) return country.byCategory[category]?.[type]?.[metric] ?? 0
  return country[type][metric]
}

export function valueToColor(value: number, max: number, type: 'imports' | 'exports'): string {
  if (max === 0) return '#1a1a2e'
  const t = Math.min(value / max, 1)
  if (type === 'imports') {
    const r = Math.round(20  + (10  - 20)  * t)
    const g = Math.round(60  + (100 - 60)  * t)
    const b = Math.round(160 + (255 - 160) * t)
    return `rgb(${r},${g},${b})`
  } else {
    const r = Math.round(180 + (255 - 180) * t)
    const g = Math.round(80  + (120 - 80)  * t)
    const b = Math.round(20  + (0   - 20)  * t)
    return `rgb(${r},${g},${b})`
  }
}

// ─── Trade flows (kept for globe arrows — uses top countries from real data) ─
export const TRADE_FLOWS: TradeFlow[] = (() => {
  const top = TRADE_DATA.slice(0, 10)
  const flows: TradeFlow[] = []
  for (let i = 0; i < Math.min(top.length, 5); i++) {
    for (let j = i + 1; j < Math.min(top.length, 6); j++) {
      const a = top[i]!
      const b = top[j]!
      flows.push({
        fromIso3: a.iso3, fromLat: a.lat, fromLng: a.lng,
        toIso3:   b.iso3, toLat:   b.lat, toLng:   b.lng,
        usd: Math.round((a.exports.usd + b.imports.usd) / 2),
        weight: 0,
        type: 'export',
      })
    }
  }
  return flows
})()

// ─── Search index ──────────────────────────────────────────────────────────

export const SEARCH_ITEMS: SearchItem[] = [
  ...TRADE_DATA.map(c => ({
    type: 'country' as const,
    label: c.name,
    path: `/countries/${c.iso3.toLowerCase()}`,
  })),
  ...CATEGORIES.map(cat => ({
    type: 'category' as const,
    label: cat,
    path: `/categories/${cat.toLowerCase().replace(/[\s&/,()]+/g, '-').replace(/-+/g, '-')}`,
  })),
  ...YEARS.map(y => ({
    type: 'year' as const,
    label: String(y),
    path: `/years/${y}`,
  })),
]
