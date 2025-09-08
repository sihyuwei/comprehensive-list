import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import unicodedata
import string

# --- Data Sources ---
HB32 = pd.read_csv('input_handbuch/HB32.csv')
HB34 = pd.read_csv('input_handbuch/HB34.csv')
HB_GmbH = pd.read_csv('input_handbuch/HB_GmbH_32.csv')

hb32_volume_links = {
    "Vol 1": "https://www.dropbox.com/scl/fi/91qw3d1lfr1gxznzngxtu/1.-Band-1-1648.pdf?rlkey=syah3x6ytq3tyktmi56josadv&st=ofswqvy5&raw=1",
    "Vol 2": "https://www.dropbox.com/scl/fi/zswrpoiy5gbolo4z6xjtn/2.-Band-1649-3472.pdf?rlkey=zd7slktunundp1q3ro8qpvvgm&st=noxgl0cu&raw=1",
    "Vol 3": "https://www.dropbox.com/scl/fi/zssvb5yk5a7fl5ltzi7dk/3.-Band-3473-5104.pdf?rlkey=n7d8lsct97jw88p5b9zo010la&st=zxq238ec&raw=1",
    "Vol 4": "https://www.dropbox.com/scl/fi/vkhqkqrp0ldfsxp6umuzy/4.-Band-5105-6759.pdf?rlkey=u2twctx63qlmar4tilcnjb3ud&st=aize0fef&raw=1"
}

hb34_volume_links = {
    "Vol 1": "https://www.dropbox.com/scl/fi/9q3lyalclyyavfs6nxe2s/Handbuch-der-deutschen-Aktiengesellschaften_1934_band_91.pdf?rlkey=9mjdidf8p8dzc2ztuv7hewebc&st=tw3sgqup&raw=1",
    "Vol 2": "https://www.dropbox.com/scl/fi/z38cbvbu4sbce6edirhfh/Handbuch-der-deutschen-Aktiengesellschaften_1934_band_92.pdf?rlkey=ne1vdi6t45fucxbrgwth641xx&st=1h6cp6ze&raw=1",
    "Vol 3": "https://www.dropbox.com/scl/fi/qsy7jthicw0hn831zv5fv/Handbuch-der-deutschen-Aktiengesellschaften_1934_band_93.pdf?rlkey=acf96s87bwit1z21s72hp4fx5&st=gjxyscyg&raw=1",
    "Vol 4": "https://www.dropbox.com/scl/fi/gds6zbgd2d9bx7agqvyj4/Handbuch-der-deutschen-Aktiengesellschaften_1934_band_94.pdf?rlkey=16j1146qxsx2hc14kx7nguh9e&st=wwv55ont&raw=1"
}

hb_gmbh_volume_links = {
    "Vol 1": "https://www.dropbox.com/scl/fi/jkg34lu5tsh7vnjk2q9b2/Handbuch_GmbH_1932.pdf?rlkey=necgm2cxc231w31u6qul0hsye&st=jlc1hzvf&raw=1"
}

sources = {
    "Handbuch AG 32": HB32,
    "Handbuch AG 34": HB34,
    "Handbuch GmbH 32": HB_GmbH,
}

def normalize_text(s: str) -> str:
    # Convert to str (in case of NaN), lowercase
    s = str(s).lower()

    # Normalize accents/umlauts
    s = ''.join(
        c for c in unicodedata.normalize('NFKD', s)
        if not unicodedata.combining(c)
    )

    # Remove punctuation and extra spaces
    s = ''.join(c for c in s if c not in string.punctuation)
    s = s.replace(" ", "")

    return s

# --- UI ---
st.title("Search Across Data Sources")

# 1. Select source
source_choice = st.radio("Choose a data source:", list(sources.keys()))
df = sources[source_choice]

# 2. Search box
query = st.text_input("Search: (case- and diacritic-insensitive)")

# --- Filter results with accent-insensitive search ---
if query:
    norm_query = normalize_text(query)
    filtered_df = df[df.apply(
        lambda row: row.astype(str).map(normalize_text).str.contains(norm_query, case=False).any(),
        axis=1
    )]
else:
    filtered_df = df

# 4. Show interactive grid
gb = GridOptionsBuilder.from_dataframe(filtered_df)
gb.configure_pagination(paginationAutoPageSize=True)
gb.configure_side_bar()
gb.configure_default_column(editable=False, groupable=True, autoSize=True)  
gb.configure_grid_options(
    enableRangeSelection=True,
    enableCellTextSelection=True,
    suppressCopySingleCellRanges=False,
    copyHeadersToClipboard=True
)
grid_options = gb.build()

AgGrid(
    filtered_df,
    gridOptions=grid_options,
    enable_enterprise_modules=False,
    fit_columns_on_grid_load=False,  # turn this OFF
    allow_unsafe_jscode=True
)
