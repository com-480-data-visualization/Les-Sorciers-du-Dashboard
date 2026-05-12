import countriesRaw  from '~/utils/generated/countries.json'
import categoriesRaw from '~/utils/generated/categories.json'
import yearsRaw      from '~/utils/generated/years.json'

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

export const CATEGORIES: string[] = [
  ...new Set((categoriesRaw as Array<{ name: string }>).map(c => c.name))
]

export const YEARS: number[] = (yearsRaw as Array<{ year: number }>).map(y => y.year)

// ─── Helper functions ──────────────────────────────────────────────────────

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
      flows.push({
        fromIso3: top[i].iso3, fromLat: top[i].lat, fromLng: top[i].lng,
        toIso3:   top[j].iso3, toLat:   top[j].lat,   toLng:   top[j].lng,
        usd: Math.round((top[i].exports.usd + top[j].imports.usd) / 2),
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
