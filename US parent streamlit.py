import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Master table (union of companies across 7 sources)

master_data = pd.read_csv('comprehensive list/list_US_parent/output/parent_union.csv')
companies = master_data['US Company']

tfr = pd.read_csv('comprehensive list/list_US_parent/output/tfr.csv')
tenenbaum = pd.read_csv('comprehensive list/list_US_parent/output/tenenbaum.csv')
moodys32 = pd.read_csv('comprehensive list/list_US_parent/output/moodys32.csv')
moodys34 = pd.read_csv('comprehensive list/list_US_parent/output/moodys34.csv')
hb32 = pd.read_csv('comprehensive list/list_US_parent/output/hb32.csv')
hb34 = pd.read_csv('comprehensive list/list_US_parent/output/hb34.csv')
hb_gmbh = pd.read_csv('comprehensive list/list_US_parent/output/hb_gmbh.csv')

# Detailed info (simulate your 7 sources)
source_tables = {
    "TFR-500": tfr,
    "Tenenbaum": tenenbaum,
    "Moodys 32": moodys32,
    "Moodys 34": moodys34,
    "HB 32": hb32,
    "HB 34": hb34,
    "HB GmbH": hb_gmbh
}

# -----------------------
# Search/filter input
# -----------------------
search_term = st.text_input("Search for a US company")
if search_term:
    filtered_master = master_data[master_data["US Company"].str.contains(search_term, case=False)]
else:
    filtered_master = master_data

# -----------------------
# Ag-Grid display
# -----------------------
gb = GridOptionsBuilder.from_dataframe(filtered_master)
gb.configure_selection(selection_mode="single", use_checkbox=False)
gb.configure_pagination(enabled=True)
grid_options = gb.build()

grid_response = AgGrid(
    filtered_master,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=300,
    fit_columns_on_grid_load=True
)

# -----------------------
# Streamlit UI
# -----------------------

st.set_page_config(layout="wide")

# Get selected row
selected = grid_response["selected_rows"]

if not selected.empty:
    selected_row = selected.iloc[0]
    company = selected_row["US Company"]

    source = st.selectbox(
        "Choose source to drill down", 
        source_tables.keys()
    )

    st.subheader(f"Details for {company} in {source}")
    if source in source_tables:
        details = source_tables[source]
        filtered = details[details["US Company"] == company]

        if not filtered.empty:
            for idx, row in filtered.iterrows():
                foreign_name = row.get("Name of Foreign Business", f"Record {idx+1}")

                reshaped = (
                    row.drop(labels=["US Company"])
                    .to_frame()
                    .reset_index()
                    .rename(columns={"index": "Attribute", 0: "Value"})
                )
                reshaped.loc[-1] = ["Company", row["US Company"]]
                reshaped.index = reshaped.index + 1
                reshaped = reshaped.sort_index()

                with st.expander(f"{foreign_name}"):
                    st.dataframe(reshaped, use_container_width=True)
        else:
            st.info("No data available for this company in this source.")
    else:
        st.warning("This source has no detail table yet.")
