import streamlit as st
import pandas as pd
import numpy as np
import re
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import unicodedata
import string

# Master table (union of companies across 7 sources)

master_data = pd.read_csv('output/all_subsidiaries_searched.csv')

presence_filters = [
    'Present in HB 32',
    'Present in HB 34',
    'Present in HB GmbH'
]

presence_source_dict = {
    'Present in HB 32': 'HB 32',
    'Present in HB 34': 'HB 34',
    'Present in HB GmbH': 'HB GmbH',
    'TFR-500': 'TFR-500',
    'Tenenbaum': 'Tenenbaum',
    'Moodys 32': 'Moodys 32',
    'Moodys 34': 'Moodys 34'
}

id_sources = [
    'TFR-500',
    'Tenenbaum',
    'Moodys 32',
    'Moodys 34',
    'IDed in HB 32',
    'IDed in HB 34',
    'IDed in HB GmbH'
]

tfr = pd.read_csv('output/tfr_cleaned.csv')
tenenbaum = pd.read_csv('output/tenenbaum_cleaned.csv')
moodys32 = pd.read_csv('output/moodys32_cleaned.csv')
moodys34 = pd.read_csv('output/moodys34_cleaned.csv')
hb32 = pd.read_csv('output/hb1932_cleaned_expanded.csv')
hb34 = pd.read_csv('output/hb1934_cleaned_expanded.csv')
hb_gmbh = pd.read_csv('output/hb_gmbh_cleaned_expanded.csv')

# Detailed info
source_tables = {
    "HB 32": hb32,
    "HB 34": hb34,
    "HB GmbH": hb_gmbh,
    "TFR-500": tfr,
    "Tenenbaum": tenenbaum,
    "Moodys 32": moodys32,
    "Moodys 34": moodys34
}

tfr_volume_links = {
    "Vol 1": "https://www.dropbox.com/scl/fi/3k3yg5apcls4z1i5xw49r/business_holding_in_Germany.pdf?rlkey=tkhqw0n0hlwq6qgppkh4fmkoz&raw=1"
}

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

moodys32_links = {
    "Vol 1": "https://www.dropbox.com/scl/fi/be5inf5m3c1f2fwb0f9cl/INDUSTRIAL_1.pdf?rlkey=w4i05a7jybrc24o8hoqzyf7mp&raw=1"
}

moodys34_links = {
    "Vol 1": "https://www.dropbox.com/scl/fi/933x06x4roacjvybgcuhk/INDUSTRIAL_1.pdf?rlkey=8oyffhktkfip5fcx84w6a0z2g&raw=1"
}

tenenbaum_links = {
    "Vol 1": "https://www.dropbox.com/scl/fi/5k2no94oivf0yyt7korqz/American-investment-and-business-interestes-in-Germany.pdf?rlkey=ha4dxanlf304is5uqkymt89jv&raw=1"
}

volume_link_dicts = {
    "HB 32": hb32_volume_links,
    "HB 34": hb34_volume_links,
    "HB GmbH": hb_gmbh_volume_links,
    "TFR-500": tfr_volume_links,
    "Tenenbaum": tenenbaum_links,
    "Moodys 32": moodys32_links,
    "Moodys 34": moodys34_links,
}

def make_pdf_link(vol_entry, source):
    match = re.match(r"(Vol \d+), p\. (\d+)", vol_entry)
    if match:
        vol, page = match.groups()
        base_url = volume_link_dicts[source].get(vol)
        if base_url:
            return f"[{vol}]( {base_url}#page={page} ), p. {page}"
    return vol_entry  # fallback if format doesn’t match

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


# -----------------------
# Start of UI
# -----------------------

st.title("German firms")

# -----------------------
# Search/filter input
# -----------------------
st.set_page_config(layout="wide")

search_term = st.text_input("Search for a German subsidiary (case- and accent-insensitive)")
if search_term:
    norm_query = normalize_text(search_term)
    filtered_master = master_data[master_data["German subsidiary"].map(normalize_text).str.contains(norm_query, case=False)]
else:
    filtered_master = master_data

# --------------------------
# Collect all types
# --------------------------

link_type_cols = [col for col in master_data if 'link_type' in col]
org_type_cols = [col for col in master_data if 'org_type' in col]

all_link_types = sorted(set().union(*[master_data[col].dropna().unique() for col in link_type_cols]))
all_org_types = sorted(set().union(*[master_data[col].dropna().unique() for col in org_type_cols]))

# --------------------------
# User selects types
# --------------------------
selected_link_types = st.multiselect("Choose link types", all_link_types, default=all_link_types)
selected_org_types = st.multiselect("Choose org types", all_org_types, default=all_org_types)

# Step 1: choose mode
filter_mode = st.radio(
    "Handbuch presence filter",
    ["Show all firms", "Limit to firms present in Handbuch"]
)

# Step 2: if limited, choose which meta sources
selected_meta = []
if filter_mode == "Limit to firms present in Handbuch":
    selected_meta = st.multiselect(
        "Firms are present in any of the following: (union)",
        presence_filters,
        default=presence_filters
    )

selected_sources = st.multiselect("Choose sources", id_sources, default=id_sources)

if selected_link_types and selected_org_types and selected_sources:
    # --------------------------
    # Union of companies
    # --------------------------
    company_set = set()
    for source in selected_sources:
        if selected_meta:
            mask = (
                filtered_master[f"{source}_link_type"].isin(selected_link_types) 
                & filtered_master[f"{source}_org_type"].isin(selected_org_types) 
                & filtered_master[selected_meta].any(axis=1)
            )
        else:
            mask = (
                filtered_master[f"{source}_link_type"].isin(selected_link_types) 
                & filtered_master[f"{source}_org_type"].isin(selected_org_types)
            )
        company_set.update(filtered_master.loc[mask, "German subsidiary"].unique())
    company_list = sorted(list(company_set))

    # --------------------------
    # Build grid
    # --------------------------

    grid = pd.DataFrame({"German subsidiary": company_list})

    for source in selected_sources:
        mask = (
            master_data[f"{source}_link_type"].isin(selected_link_types)
            & master_data[f"{source}_org_type"].isin(selected_org_types)
        )
        grid[source] = grid["German subsidiary"].isin(master_data.loc[mask, "German subsidiary"])

    for presence_filter in presence_filters:
        grid[presence_filter] = grid["German subsidiary"].isin(master_data.loc[master_data[presence_filter], "German subsidiary"])

    # filtered_grid = grid[grid['German subsidiary'].isin(company_list)]
    grid_data = grid[['German subsidiary'] + presence_filters + selected_sources]
    

    # # Add total companies
    # st.subheader(f"Total companies in union: {grid_data.shape[0]}")

    # --------------------------
    # Show result
    # --------------------------

    # ---------------------
    # Interactive grid
    gb = GridOptionsBuilder.from_dataframe(grid_data)
    gb.configure_default_column(
        filter=True,  # enable filtering
        sortable=True,
        resizable=True
    )
    gb.configure_selection("single", use_checkbox=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        grid_data,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=400,
        fit_columns_on_grid_load=True,
    )

    # Extract filtered data
    filtered_df = pd.DataFrame(grid_response["data"])

    # Show total companies in *filtered* view
    st.subheader(f"Total companies in filtered view: {filtered_df.shape[0]}")

    # -----------------------
    # Streamlit UI
    # -----------------------

    # st.set_page_config(layout="wide")

    # Get selected row
    selected = grid_response["selected_rows"]

    if selected is not None and not selected.empty:
        selected_row = selected.iloc[0]
        company = selected_row["German subsidiary"]

        source = st.selectbox(
            "Choose source to drill down", 
            [value for key, value in presence_source_dict.items() if selected_row[key]]
        )

        st.subheader(f"Details for {company} in {source}")
        if source in source_tables:
            details = source_tables[source]
            filtered = details[details["German subsidiary"] == company]

            if not filtered.empty:
                for idx, row in filtered.iterrows():
                    foreign_name = row.get("US Company", f"Record {idx+1}")

                    reshaped = pd.DataFrame({
                        "Attribute": row.drop(labels=["German subsidiary"]).index,
                        "Value": row.drop(labels=["German subsidiary"]).values
                    })

                    # Add the German subsidiary as the first row
                    reshaped.loc[-1] = ["German subsidiary", row["German subsidiary"]]
                    reshaped.index = reshaped.index + 1
                    reshaped = reshaped.sort_index()

                    # # Convert DataFrame into Markdown so links work
                    # markdown_table = reshaped.to_markdown(index=False)

                    with st.expander(f"Parent: {foreign_name}"):
                        st.dataframe(reshaped, width="stretch")

                        vol_entry = row.get("Vol", None)
                        if pd.notna(vol_entry):
                            pdf_link = make_pdf_link(vol_entry, source)
                            if pdf_link.startswith("["):  
                                url = pdf_link.split('](')[1][:-1]
                                st.link_button(f"📖 Open PDF {source} {vol_entry}", url)
            else:
                st.info("No data available for this company in this source.")
        else:
            st.warning("This source has no detail table yet.")
    else:
        st.warning("Click on a company to see the details.")

else:
    st.warning("Please select at least one link type, one org type, and one source.")