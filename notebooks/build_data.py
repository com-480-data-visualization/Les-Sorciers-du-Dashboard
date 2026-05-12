"""
GeoFlux data builder – generates 4 JSON files consumed by the Nuxt app.
Run from the notebooks/ directory:   python build_data.py
"""

import pandas as pd
import numpy as np
import json
import re
from pathlib import Path
import pycountry
from shapely.geometry import shape

# ── Paths ──────────────────────────────────────────────────────────────────
GEOJSON_PATH = '../public/geojson/countries.geojson'
OUT_DIR      = Path('../app/utils/generated')
OUT_DIR.mkdir(exist_ok=True)

SNAPSHOT_YEAR = 2016
YEARS = list(range(1988, 2017))

# ── Category mapping ───────────────────────────────────────────────────────
CATEGORY_NAMES = {
    '01': 'Live Animals',            '02': 'Meat',
    '03': 'Fish & Seafood',          '04': 'Dairy, Eggs & Honey',
    '05': 'Other Animal Products',   '06': 'Live Plants & Flowers',
    '07': 'Vegetables',              '08': 'Fruits & Nuts',
    '09': 'Coffee, Tea & Spices',    '10': 'Cereals',
    '11': 'Milling Products',        '12': 'Oilseeds',
    '13': 'Plant Extracts',          '14': 'Vegetable Materials',
    '15': 'Fats & Oils',             '16': 'Meat & Fish Preparations',
    '17': 'Sugar',                   '18': 'Cocoa & Chocolate',
    '19': 'Cereal Preparations',     '20': 'Vegetable Preparations',
    '21': 'Miscellaneous Food',      '22': 'Beverages & Spirits',
    '23': 'Animal Feed',             '24': 'Tobacco',
    '25': 'Salt, Stone & Cement',    '26': 'Ores & Minerals',
    '27': 'Mineral Fuels & Oils',    '28': 'Inorganic Chemicals',
    '29': 'Organic Chemicals',       '30': 'Pharmaceuticals',
    '31': 'Fertilizers',             '32': 'Dyes & Pigments',
    '33': 'Cosmetics & Perfumes',    '34': 'Soaps & Waxes',
    '35': 'Albumins & Enzymes',      '36': 'Explosives',
    '37': 'Photographic Goods',      '38': 'Miscellaneous Chemicals',
    '39': 'Plastics',                '40': 'Rubber',
    '41': 'Hides & Leather',         '42': 'Leather Articles',
    '43': 'Furskins',                '44': 'Wood',
    '45': 'Cork',                    '46': 'Basketwork',
    '47': 'Wood Pulp',               '48': 'Paper & Paperboard',
    '49': 'Books & Printed Matter',  '50': 'Silk',
    '51': 'Wool & Animal Hair',      '52': 'Cotton',
    '53': 'Vegetable Textile Fibres','54': 'Manmade Filaments',
    '55': 'Manmade Staple Fibres',   '56': 'Wadding & Felt',
    '57': 'Carpets',                 '58': 'Special Woven Fabrics',
    '59': 'Coated Textiles',         '60': 'Knitted Fabrics',
    '61': 'Apparel (Knit)',          '62': 'Apparel (Woven)',
    '63': 'Other Textiles',          '64': 'Footwear',
    '65': 'Headgear',                '66': 'Umbrellas & Walking Sticks',
    '67': 'Feathers & Artificial Flowers', '68': 'Stone & Plaster Articles',
    '69': 'Ceramics',                '70': 'Glass & Glassware',
    '71': 'Precious Stones & Metals','72': 'Iron & Steel',
    '73': 'Iron & Steel Articles',   '74': 'Copper',
    '75': 'Nickel',                  '76': 'Aluminium',
    '78': 'Lead',                    '79': 'Zinc',
    '80': 'Tin',                     '81': 'Other Base Metals',
    '82': 'Metal Tools',             '83': 'Miscellaneous Metal Articles',
    '84': 'Industrial Machinery',    '85': 'Electrical Equipment',
    '86': 'Railway Equipment',       '87': 'Vehicles',
    '88': 'Aircraft',                '89': 'Ships & Boats',
    '90': 'Optical & Medical Equipment', '91': 'Clocks & Watches',
    '92': 'Musical Instruments',     '93': 'Arms & Ammunition',
    '94': 'Furniture',               '95': 'Toys & Sports',
    '96': 'Miscellaneous Manufactured', '97': 'Art & Collectibles',
}

HISTORICAL_NOTES = {
    1988: 'The Uruguay Round of GATT negotiations was in full swing, laying the groundwork for the future WTO. Global trade volumes grew steadily amid broad economic expansion.',
    1989: 'The fall of the Berlin Wall reshaped trade patterns in Europe as Eastern economies began opening to world markets. Asian economies continued their rapid export-led growth.',
    1990: "Iraq's invasion of Kuwait triggered an oil price spike that disrupted global commodity trade. The US entered a mild recession, dampening import demand.",
    1991: 'Collapse of the Soviet Union created new trading partners and disrupted established flows. Gulf War resolution allowed oil markets to stabilize.',
    1992: 'The European Single Market officially launched, dramatically easing intra-EU trade barriers. NAFTA negotiations concluded, promising deeper North American integration.',
    1993: 'NAFTA was signed and ratified. Uruguay Round negotiations succeeded, paving the way for the WTO. Global growth remained subdued following the early-1990s slowdown.',
    1994: "The WTO agreement was signed in Marrakesh. Mexico's peso crisis at year-end sent shockwaves through emerging markets and curbed Latin American trade.",
    1995: 'WTO officially replaced GATT, marking a new era of rules-based multilateral trade. Global trade volumes grew at their fastest pace since the 1970s.',
    1996: 'Robust economic growth across the Asia-Pacific drove commodity and manufactured goods trade to new highs. Information technology exports surged.',
    1997: 'Asian financial crisis erupted in Thailand and spread across the region, causing dramatic currency depreciations and sharp trade contractions in Southeast and East Asia.',
    1998: 'Russia defaulted on its debt, amplifying the Asian crisis contagion. Commodity prices collapsed. Global trade growth slowed sharply despite continued US strength.',
    1999: 'The euro launched as an accounting currency among 11 EU members. Asian economies began recovering. The WTO Seattle ministerial ended in failure amid mass protests.',
    2000: "Dot-com boom peaked; global trade hit record growth rates. China's WTO accession negotiations concluded. Oil prices recovered from their 1998 lows.",
    2001: "September 11 attacks disrupted US and global trade. The dot-com bust caused a global recession. China officially joined the WTO in December, a watershed moment.",
    2002: "Euro coins and notes entered circulation. Slow global recovery underway. China's WTO membership accelerated its integration into global supply chains.",
    2003: "Iraq War and SARS outbreak disrupted regional trade, especially in Asia. Chinese manufacturing exports continued their dramatic rise as a global factory.",
    2004: "EU expanded to 25 members, integrating Central and Eastern European trade flows. China's export boom accelerated, driving global commodity demand upward.",
    2005: "China became the world's third-largest trading nation. Rising commodity prices boosted exporters of oil, metals, and agricultural goods across the developing world.",
    2006: 'Global trade grew 8% in volume terms. The commodity supercycle intensified. Doha Round negotiations stalled, highlighting tensions between rich and developing nations.',
    2007: 'Global trade reached record levels before the financial crisis struck in H2. The US subprime mortgage crisis began spreading beyond its borders.',
    2008: "Global financial crisis intensified after Lehman Brothers' collapse in September. Trade finance dried up and orders collapsed; world trade volumes fell sharply in Q4.",
    2009: "World trade fell by approximately 12%—the largest single-year decline since World War II—as the Great Recession crushed demand and supply chains froze.",
    2010: "Powerful V-shaped recovery: world trade volumes grew ~14%. China overtook Germany as the world's largest exporter. Commodity prices rebounded strongly.",
    2011: "Japan's earthquake and tsunami disrupted global electronics and auto supply chains. The Arab Spring affected MENA trade patterns. Commodity prices remained elevated.",
    2012: 'Eurozone debt crisis peaked, suppressing European import demand. Global trade growth slowed to just 2%. Emerging markets showed remarkable resilience.',
    2013: 'Fed tapering fears roiled emerging market currencies and capital flows. Global trade growth remained sluggish at 2.5% despite recovery in developed economies.',
    2014: 'Oil price collapse began in H2, reshaping global energy trade. Russia–Ukraine conflict triggered Western sanctions affecting Eastern European trade flows.',
    2015: "Oil and commodity prices crashed further, reducing the USD value of resource exports dramatically. China's slowdown raised fears of a global growth drag.",
    2016: 'Brexit vote in June created UK trade policy uncertainty. US–China trade tensions began emerging. Global trade growth near zero—the weakest since the 2008–09 crisis.',
}

MANUAL_ISO3 = {
    'EU-28': None, 'Other Africa': None, 'Other America': None,
    'Other Asia': None, 'Other Europe': None, 'Other Oceania': None,
    'Areas, nes': None, 'Free Zones': None, 'Bunkers': None,
    'LAIA, nes': None, 'CACM, nes': None, 'Oceania, nes': None,
    'Eastern Europe, nes': None, 'Special Categories': None,
    'Fmr Dem. Rep. of Germany': None, 'Fmr Fed. Rep. of Germany': None,
    'Fmr Ethiopia': None, 'Fmr Sudan': None, 'Fmr Yugoslavia': None,
    'Fmr USSR': None, 'Fmr Czechoslovakia': None,
    'Sudan (former)': None, 'Serbia and Montenegro': None,
    'Czechoslovakia': None, 'Yugoslavia': None, 'Netherlands Antilles': None,
    'China, Hong Kong SAR': 'HKG', 'China, Macao SAR': 'MAC',
    'China, Taiwan Province of': 'TWN', 'Taiwan Province of China': 'TWN',
    'United States of America': 'USA', 'United Kingdom': 'GBR',
    'Republic of Korea': 'KOR', 'Dem. Rep. of the Congo': 'COD',
    "Dem. People's Republic of Korea": 'PRK',
    'Bolivia (Plurinational State of)': 'BOL',
    'Iran (Islamic Republic of)': 'IRN',
    "Lao People's Dem. Rep.": 'LAO',
    'Micronesia (Federated States of)': 'FSM',
    'Republic of Moldova': 'MDA', 'Russian Federation': 'RUS',
    'State of Palestine': 'PSE', 'Syrian Arab Republic': 'SYR',
    'Tanzania, United Republic of': 'TZA', 'United Republic of Tanzania': 'TZA',
    'Venezuela (Bolivarian Republic of)': 'VEN', 'Viet Nam': 'VNM',
    'Trinidad and Tobago': 'TTO', 'Brunei Darussalam': 'BRN',
    'Cabo Verde': 'CPV', 'Timor-Leste': 'TLS', 'Belgium-Luxembourg': 'BEL',
    'China': 'CHN', 'Congo': 'COG', 'Gambia': 'GMB', 'Guinea-Bissau': 'GNB',
    'Netherlands': 'NLD', "Côte d'Ivoire": 'CIV', "CÃ´te d'Ivoire": 'CIV',
    'Réunion': 'REU', 'Saint Lucia': 'LCA',
    'Saint Vincent and the Grenadines': 'VCT', 'Sao Tome and Principe': 'STP',
}

_iso3_cache = {}

def get_iso3(name):
    if name in _iso3_cache:
        return _iso3_cache[name]
    if name in MANUAL_ISO3:
        _iso3_cache[name] = MANUAL_ISO3[name]
        return MANUAL_ISO3[name]
    try:
        r = pycountry.countries.lookup(name).alpha_3
    except LookupError:
        r = None
    _iso3_cache[name] = r
    return r

def make_slug(name):
    return re.sub(r'-+', '-', re.sub(r'[\s&/,()]+', '-', name.lower())).strip('-')

def raw_cat_to_name(raw):
    code = raw.split('_')[0].zfill(2)
    return CATEGORY_NAMES.get(code)

def rounded(x):
    return int(round(float(x)))

def agg_flows_df(src, group_cols):
    agg = (
        src.groupby(group_cols + ['flow'])[['usd_m', 'wt_m']]
        .sum()
        .unstack('flow', fill_value=0)
    )
    agg.columns = ['_'.join(c) for c in agg.columns]
    for col in ['usd_m_Import', 'usd_m_Export', 'wt_m_Import', 'wt_m_Export']:
        if col not in agg.columns:
            agg[col] = 0.0
    return agg.reset_index()

# ── Load GeoJSON centroids ─────────────────────────────────────────────────
print('Loading GeoJSON...')
with open(GEOJSON_PATH) as f:
    geojson = json.load(f)

iso3_coords = {}
for feature in geojson['features']:
    iso3 = feature['properties'].get('ISO3166-1-Alpha-3')
    if iso3:
        try:
            centroid = shape(feature['geometry']).centroid
            iso3_coords[iso3] = {'lat': round(centroid.y, 2), 'lng': round(centroid.x, 2)}
        except Exception:
            pass
print(f'  {len(iso3_coords)} centroids loaded')

# ── Load CSV ───────────────────────────────────────────────────────────────
print('Loading CSV...')
import kagglehub
from kagglehub import KaggleDatasetAdapter

df = kagglehub.dataset_load(
    KaggleDatasetAdapter.PANDAS,
    'unitednations/global-commodity-trade-statistics',
    'commodity_trade_statistics_data.csv',
    pandas_kwargs={'dtype': {'comm_code': str}, 'low_memory': False}
)
print(f'  {len(df):,} rows loaded')

# ── Clean ──────────────────────────────────────────────────────────────────
print('Cleaning...')
df = df[~df['category'].isin(['all_commodities', '99_commodities_not_specified_according_to_kind'])].copy()
df['cat_name'] = df['category'].apply(raw_cat_to_name)
df = df.dropna(subset=['cat_name'])
df = df[df['flow'].isin(['Import', 'Export'])]

# Map country → ISO3
unique_names  = df['country_or_area'].unique()
name_to_iso3  = {n: get_iso3(n) for n in unique_names}
df['iso3']    = df['country_or_area'].map(name_to_iso3)
df = df.dropna(subset=['iso3'])
df = df[df['iso3'].str.len() == 3]

df['weight_kg'] = df['weight_kg'].fillna(0)
df['usd_m']     = df['trade_usd'] / 1_000_000
df['wt_m']      = df['weight_kg'] / 1_000_000
df['comm_code'] = df['comm_code'].str.strip().str.zfill(6)

iso3_names = (
    df[['iso3', 'country_or_area']].drop_duplicates()
    .groupby('iso3')['country_or_area'].first().to_dict()
)
print(f'  {len(df):,} rows kept, {df["iso3"].nunique()} countries')

df_snap = df[df['year'] == SNAPSHOT_YEAR].copy()

# ── countries.json ─────────────────────────────────────────────────────────
print('Building countries.json...')
snap_country = agg_flows_df(df_snap, ['iso3'])
snap_cat     = agg_flows_df(df_snap, ['iso3', 'cat_name'])
series_df    = agg_flows_df(df,      ['iso3', 'year'])

countries_out = []
for _, row in snap_country.iterrows():
    iso3   = row['iso3']
    coords = iso3_coords.get(iso3, {'lat': 0.0, 'lng': 0.0})

    by_cat = {}
    for _, cr in snap_cat[snap_cat['iso3'] == iso3].iterrows():
        iu = rounded(cr['usd_m_Import']); eu = rounded(cr['usd_m_Export'])
        if iu > 0 or eu > 0:
            by_cat[cr['cat_name']] = {
                'imports': {'usd': iu,  'weight': rounded(cr['wt_m_Import'])},
                'exports': {'usd': eu,  'weight': rounded(cr['wt_m_Export'])},
            }

    yr_rows = series_df[series_df['iso3'] == iso3].sort_values('year')
    series = [
        {
            'year': int(yr['year']),
            'imports': {'usd': rounded(yr['usd_m_Import']), 'weight': rounded(yr['wt_m_Import'])},
            'exports': {'usd': rounded(yr['usd_m_Export']), 'weight': rounded(yr['wt_m_Export'])},
        }
        for _, yr in yr_rows.iterrows()
    ]

    countries_out.append({
        'iso3':       iso3,
        'name':       iso3_names.get(iso3, iso3),
        'lat':        coords['lat'],
        'lng':        coords['lng'],
        'imports':    {'usd': rounded(row['usd_m_Import']), 'weight': rounded(row['wt_m_Import'])},
        'exports':    {'usd': rounded(row['usd_m_Export']), 'weight': rounded(row['wt_m_Export'])},
        'byCategory': by_cat,
        'series':     series,
    })

countries_out.sort(key=lambda c: c['imports']['usd'] + c['exports']['usd'], reverse=True)
with open(OUT_DIR / 'countries.json', 'w') as f:
    json.dump(countries_out, f, separators=(',', ':'))
sz = (OUT_DIR / 'countries.json').stat().st_size // 1024
print(f'  countries.json → {len(countries_out)} countries, {sz} KB')

# ── categories.json ────────────────────────────────────────────────────────
print('Building categories.json...')
snap_cat_world = agg_flows_df(df_snap, ['cat_name'])
series_cat_df  = agg_flows_df(df,      ['cat_name', 'year'])
code_for_name  = {v: k for k, v in CATEGORY_NAMES.items()}

categories_out = []
for _, row in snap_cat_world.iterrows():
    name    = row['cat_name']
    yr_rows = series_cat_df[series_cat_df['cat_name'] == name].sort_values('year')
    series  = [
        {
            'year': int(yr['year']),
            'imports': {'usd': rounded(yr['usd_m_Import']), 'weight': rounded(yr['wt_m_Import'])},
            'exports': {'usd': rounded(yr['usd_m_Export']), 'weight': rounded(yr['wt_m_Export'])},
        }
        for _, yr in yr_rows.iterrows()
    ]
    categories_out.append({
        'id':      make_slug(name),
        'code':    code_for_name.get(name, ''),
        'name':    name,
        'imports': {'usd': rounded(row['usd_m_Import']), 'weight': rounded(row['wt_m_Import'])},
        'exports': {'usd': rounded(row['usd_m_Export']), 'weight': rounded(row['wt_m_Export'])},
        'series':  series,
    })

categories_out.sort(key=lambda c: c['imports']['usd'] + c['exports']['usd'], reverse=True)
with open(OUT_DIR / 'categories.json', 'w') as f:
    json.dump(categories_out, f, separators=(',', ':'))
sz = (OUT_DIR / 'categories.json').stat().st_size // 1024
print(f'  categories.json → {len(categories_out)} categories, {sz} KB')

# ── commodities.json ───────────────────────────────────────────────────────
print('Building commodities.json...')
comm_names = (
    df.groupby('comm_code')['commodity']
    .agg(lambda x: x.value_counts().index[0])
    .to_dict()
)
comm_cats = df.groupby('comm_code')['cat_name'].first().to_dict()

top_codes = (
    df.groupby('comm_code')['usd_m'].sum()
    .nlargest(500).index.tolist()
)
df_top = df[df['comm_code'].isin(top_codes)]

snap_comm = agg_flows_df(df_top[df_top['year'] == SNAPSHOT_YEAR], ['comm_code'])
series_comm_df = agg_flows_df(df_top, ['comm_code', 'year'])

commodities_out = []
for _, row in snap_comm.iterrows():
    code = row['comm_code']
    yr_rows = series_comm_df[series_comm_df['comm_code'] == code].sort_values('year')
    series  = [
        {
            'year': int(yr['year']),
            'imports': {'usd': rounded(yr['usd_m_Import']), 'weight': rounded(yr['wt_m_Import'])},
            'exports': {'usd': rounded(yr['usd_m_Export']), 'weight': rounded(yr['wt_m_Export'])},
        }
        for _, yr in yr_rows.iterrows()
    ]
    commodities_out.append({
        'id':        code,
        'comm_code': code,
        'name':      comm_names.get(code, code),
        'category':  comm_cats.get(code, ''),
        'imports':   {'usd': rounded(row['usd_m_Import']), 'weight': rounded(row['wt_m_Import'])},
        'exports':   {'usd': rounded(row['usd_m_Export']), 'weight': rounded(row['wt_m_Export'])},
        'series':    series,
    })

commodities_out.sort(key=lambda c: c['imports']['usd'] + c['exports']['usd'], reverse=True)
with open(OUT_DIR / 'commodities.json', 'w') as f:
    json.dump(commodities_out, f, separators=(',', ':'))
sz = (OUT_DIR / 'commodities.json').stat().st_size // 1024
print(f'  commodities.json → {len(commodities_out)} commodities, {sz} KB')

# ── years.json ─────────────────────────────────────────────────────────────
print('Building years.json...')
series_year_df    = agg_flows_df(df, ['year'])
series_yr_cat_df  = agg_flows_df(df, ['year', 'cat_name'])
series_yr_ctry_df = agg_flows_df(df, ['year', 'iso3'])

years_out = []
for year in YEARS:
    yr_row = series_year_df[series_year_df['year'] == year]
    if yr_row.empty:
        continue
    yr_row = yr_row.iloc[0]

    yr_cats  = series_yr_cat_df[series_yr_cat_df['year'] == year]
    yr_ctry  = series_yr_ctry_df[series_yr_ctry_df['year'] == year]

    def top5_cats(col):
        return [
            {'id': make_slug(r['cat_name']), 'name': r['cat_name'], 'usd': rounded(r[col])}
            for _, r in yr_cats.nlargest(5, col)[['cat_name', col]].iterrows()
        ]

    def top5_ctry(col):
        return [
            {'iso3': r['iso3'], 'name': iso3_names.get(r['iso3'], r['iso3']), 'usd': rounded(r[col])}
            for _, r in yr_ctry.nlargest(5, col)[['iso3', col]].iterrows()
        ]

    years_out.append({
        'year':                year,
        'imports':             {'usd': rounded(yr_row['usd_m_Import']), 'weight': rounded(yr_row['wt_m_Import'])},
        'exports':             {'usd': rounded(yr_row['usd_m_Export']), 'weight': rounded(yr_row['wt_m_Export'])},
        'topImportCategories': top5_cats('usd_m_Import'),
        'topExportCategories': top5_cats('usd_m_Export'),
        'topImportCountries':  top5_ctry('usd_m_Import'),
        'topExportCountries':  top5_ctry('usd_m_Export'),
        'historicalNote':      HISTORICAL_NOTES.get(year, ''),
    })

with open(OUT_DIR / 'years.json', 'w') as f:
    json.dump(years_out, f, separators=(',', ':'))
sz = (OUT_DIR / 'years.json').stat().st_size // 1024
print(f'  years.json → {len(years_out)} years, {sz} KB')

# ── Summary ────────────────────────────────────────────────────────────────
total_kb = sum(
    (OUT_DIR / fn).stat().st_size
    for fn in ['countries.json', 'categories.json', 'commodities.json', 'years.json']
) // 1024
print(f'\nDone. Total: {total_kb} KB across 4 files.')
