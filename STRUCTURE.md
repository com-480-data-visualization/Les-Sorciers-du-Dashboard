## App Architecture

The app is a Nuxt 3 SPA built around a full-screen Mapbox 3D globe (`layouts/canvas.vue`). Clicking a country or using the search palette opens detail pages that slide over the globe via `PageWindow.vue`. All data comes from pre-generated JSON files in `utils/generated/`.

---

### Directory Structure

```
app/
├── app.vue                          # Root layout provider
├── assets/css/main.css              # Tailwind + Nuxt UI styles
├── layouts/
│   └── canvas.vue                   # Full-screen Mapbox globe layout
├── middleware/
│   └── validateSlug.ts              # Route guard for all dynamic routes
├── pages/
│   ├── index.vue                    # Home: globe + map controls + search
│   ├── global.vue                   # World-level trade dashboard
│   ├── years/[slug].vue             # Year snapshot (/years/2016)
│   ├── countries/[slug].vue         # Country overview (/countries/usa)
│   ├── imports/[slug].vue           # Country import breakdown
│   ├── exports/[slug].vue           # Country export breakdown
│   ├── categories/[slug].vue        # HS category detail
│   └── commodities/[slug].vue       # Single commodity detail
├── components/
│   ├── PageWindow.vue               # Modal-like wrapper for all detail pages
│   ├── SearchBar.vue                # Search palette (countries, categories, commodities, years)
│   ├── StatCard.vue                 # Stat display tile with optional expand
│   ├── YearSlider.vue               # Year range slider (1988–2016)
│   └── d3/
│       ├── BarChart.vue             # Horizontal bar chart
│       ├── LineChart.vue            # Multi-series time-series line chart
│       └── PieChart.vue             # Donut chart
├── composables/
│   ├── useTradeState.ts             # Shared map control state (toggles, metric, category)
│   └── useNavHistory.ts             # Breadcrumb navigation stack
└── utils/
    ├── dummyData.ts                 # Loads countries.json + years.json; exports helpers & search index
    ├── tradeExtended.ts             # Loads commodities.json + categories.json; exports lookup helpers
    ├── formatters.ts                # Currency/weight formatters + slug converters
    └── generated/
        ├── countries.json
        ├── categories.json
        ├── commodities.json
        └── years.json
```

---

### Pages & Routes

| Route | File | Description |
|-------|------|-------------|
| `/` | `pages/index.vue` | Home page — Mapbox globe with import/export toggles, metric selector, category filter, and search |
| `/global` | `pages/global.vue` | World totals — top importing/exporting countries and categories |
| `/years/:year` | `pages/years/[slug].vue` | Snapshot for a specific year: totals, top categories/countries, historical context note |
| `/countries/:iso3` | `pages/countries/[slug].vue` | Country overview: balance, imports/exports totals, category pie chart, evolution line chart |
| `/imports/:iso3` | `pages/imports/[slug].vue` | Country import breakdown: value, weight, growth since 1988, world share — all with year slider |
| `/exports/:iso3` | `pages/exports/[slug].vue` | Country export breakdown: same stats as imports but for exports |
| `/categories/:slug` | `pages/categories/[slug].vue` | HS category: top importing/exporting countries bar charts, commodity grid, evolution chart |
| `/commodities/:id` | `pages/commodities/[slug].vue` | Single commodity: top countries bar charts, value/weight/growth stats, evolution chart |

All dynamic routes are validated by `middleware/validateSlug.ts`, which redirects to `/` on invalid slugs.

---

### Components

#### `PageWindow.vue`
Wrapper rendered over the globe for every detail page. Displays a breadcrumb trail from `useNavHistory()` and a close button that returns to `/`. All detail page content goes in its default slot.

**Props:** `title: string`

---

#### `StatCard.vue`
Reusable stat tile used throughout detail pages.

**Props:**
| Prop | Type | Description |
|------|------|-------------|
| `title` | `string` | Card label |
| `value` | `string?` | Large displayed value |
| `subtitle` | `string?` | Secondary label |
| `color` | `'blue' \| 'orange' \| 'green' \| 'red' \| 'default'` | Value color |
| `expandable` | `boolean?` | Show expand toggle |
| `clickable` | `boolean?` | Enable click-to-expand |

---

#### `YearSlider.vue`
`<input type="range">` bound via `v-model` to select a year between 1988 and 2016. Used on import/export/commodity/category pages to scrub through historical values.

**Props:** `modelValue: number` | **Emits:** `update:modelValue`

---

#### `SearchBar.vue`
Search-as-you-type palette with keyboard navigation. Results are grouped into Countries, Categories, Commodities, and Years. Navigates via `useRouter().push()` on selection.

---

#### `BarChart.vue` (D3)
Responsive horizontal bar chart. Bars are clickable.

**Props:** `data: { label, value, color? }[]`, `formatValue?: fn`, `onBarClick?: fn`

---

#### `LineChart.vue` (D3)
Multi-series line chart with axes, gridlines, and legend. Used for evolution-over-time panels.

**Props:** `series: { id, label, color, data: { year, value }[] }[]`, `yLabel?: string`, `formatY?: fn`

---

#### `PieChart.vue` (D3)
Donut chart with hover enlargement and click callbacks. Used for the category breakdown on the country page.

**Props:** `slices: { id, label, value, color? }[]`, `onSliceClick?: fn`

---

### Composables

#### `useTradeState.ts`
Shared reactive state for the globe map controls. Read by `canvas.vue` to update map layers; written by `index.vue` controls.

| State | Type | Default |
|-------|------|---------|
| `showImports` | `boolean` | `false` |
| `showExports` | `boolean` | `false` |
| `metric` | `'usd' \| 'weight'` | `'usd'` |
| `selectedCategory` | `string \| null` | `null` |
| `showFlows` | `boolean` | `false` |

---

#### `useNavHistory.ts`
Breadcrumb stack for detail page navigation. `PageWindow.vue` reads the stack to render the trail; pages call `push()` to navigate while preserving history.

| Method | Description |
|--------|-------------|
| `push(path, currentLabel)` | Add current route to stack, navigate to `path` |
| `goBack()` | Pop stack and navigate to previous route |
| `jumpTo(index)` | Truncate stack at `index` and navigate |
| `clear()` | Empty the stack |

---

### Utilities

#### `dummyData.ts`
Loads `countries.json` and `years.json`. Main exports:
- `TRADE_DATA` — all country objects
- `CATEGORIES` — unique category name list
- `YEARS` — available year list
- `SEARCH_ITEMS` — flattened search index (countries + categories + years)
- `getCountry(iso3)` — country lookup
- `getTradeValue(country, type, metric, category)` — single value accessor
- `valueToColor(value, max, type)` — RGB color for map choropleth (blue = imports, orange = exports)
- `TRADE_FLOWS` — top 10 country-to-country export connections (used for globe arc layer)

#### `tradeExtended.ts`
Loads `commodities.json` and `categories.json`. Main exports:
- `COMMODITIES` — all commodity objects
- `getCommodityById(id)`
- `getCommoditiesByCategory(category)`
- `getCountryYearlySeries(country)` — yearly import/export points for a country
- `getCategoryYearlySeries(category)` — yearly points for a category
- `getCommodityYearlySeries(commodity)` — yearly points for a commodity
- `getYearSnapshot(year)` — full year aggregate (totals, top 5 categories/countries, historical note)

#### `formatters.ts`
- `formatUsd(value)` — millions → `$3.20T` / `$450B` / `$12M`
- `formatWeight(value)` — million kg → `Gt` / `Mt` / `kt`
- `formatPercent(value)` — `12.5%`
- `formatGrowth(value)` — `+12.5%`
- `categoryToSlug(cat)` / `slugToCategory(slug, categories)` — slug conversion for categories
- `commodityToSlug(name)` / `slugToCommodityName(slug, allNames)` — slug conversion for commodities

---

### Data Flow

```
utils/generated/*.json
        │
        ├── dummyData.ts  ──► TRADE_DATA, SEARCH_ITEMS, TRADE_FLOWS
        └── tradeExtended.ts ► COMMODITIES, year/category/commodity series

useTradeState.ts ◄──► index.vue (controls) + canvas.vue (globe rendering)
useNavHistory.ts ◄──► PageWindow.vue (breadcrumbs) + all detail pages (push/back)
```

All pages are client-side computed — there is no server-side API. Every stat (growth, world share, top N) is derived at runtime from the pre-generated JSON.




## Generated Data Files

`build_data.py` produces 4 JSON files in `app/utils/generated/`, sourced from the UN Global Commodity Trade Statistics dataset (Kaggle). All monetary values are in **millions of USD**, weights in **millions of kg**, rounded to integers. The snapshot year for top-level totals is **2016**; `series` arrays span **1988–2016**.

---

### `countries.json`

Array of country objects, sorted by total trade volume (imports + exports).

| Field | Type | Description |
|-------|------|-------------|
| `iso3` | string | ISO 3166-1 Alpha-3 code (e.g. `"USA"`) |
| `name` | string | Country display name |
| `lat` | number | Centroid latitude (derived from GeoJSON) |
| `lng` | number | Centroid longitude (derived from GeoJSON) |
| `imports.usd` | number | Total imports, millions USD (2016) |
| `imports.weight` | number | Total import weight, million kg (2016) |
| `exports.usd` | number | Total exports, millions USD (2016) |
| `exports.weight` | number | Total export weight, million kg (2016) |
| `byCategory` | object | Per-category breakdown keyed by category name → `{ imports: {usd, weight}, exports: {usd, weight} }` |
| `series` | array | Year-by-year totals: `{ year, imports: {usd, weight}, exports: {usd, weight} }` |

Countries with no ISO3 match (regional aggregates, historical states like USSR) are excluded.

---

### `categories.json`

Array of HS chapter category objects (96 categories), sorted by total trade volume.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | URL slug (e.g. `"mineral-fuels-oils"`) |
| `code` | string | 2-digit HS chapter code (e.g. `"27"`) |
| `name` | string | Human-readable category name |
| `imports.usd` | number | World total imports, millions USD (2016) |
| `imports.weight` | number | World total import weight, million kg (2016) |
| `exports.usd` | number | World total exports, millions USD (2016) |
| `exports.weight` | number | World total export weight, million kg (2016) |
| `series` | array | Year-by-year world totals: `{ year, imports: {usd, weight}, exports: {usd, weight} }` |

---

### `commodities.json`

Array of the **top 500 commodities** by all-time total trade value, sorted by 2016 trade volume.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Same as `comm_code` |
| `comm_code` | string | 6-digit HS commodity code (zero-padded) |
| `name` | string | Most common commodity description from raw data |
| `category` | string | Parent category name |
| `imports.usd` | number | Total imports, millions USD (2016) |
| `imports.weight` | number | Total import weight, million kg (2016) |
| `exports.usd` | number | Total exports, millions USD (2016) |
| `exports.weight` | number | Total export weight, million kg (2016) |
| `series` | array | Year-by-year totals: `{ year, imports: {usd, weight}, exports: {usd, weight} }` |

---

### `years.json`

One entry per year from 1988 to 2016, covering world-level trade aggregates.

| Field | Type | Description |
|-------|------|-------------|
| `year` | number | The year |
| `imports.usd` | number | World total imports, millions USD |
| `imports.weight` | number | World total import weight, million kg |
| `exports.usd` | number | World total exports, millions USD |
| `exports.weight` | number | World total export weight, million kg |
| `topImportCategories` | array | Top 5 categories by import USD: `{ id, name, usd }` |
| `topExportCategories` | array | Top 5 categories by export USD: `{ id, name, usd }` |
| `topImportCountries` | array | Top 5 countries by import USD: `{ iso3, name, usd }` |
| `topExportCountries` | array | Top 5 countries by export USD: `{ iso3, name, usd }` |
| `historicalNote` | string | Contextual note about that year's global trade environment |
