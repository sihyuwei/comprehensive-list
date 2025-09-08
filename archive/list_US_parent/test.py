import streamlit as st

st.title("Open Large PDF on Specific Page")

pdf_url = "https://www.dropbox.com/scl/fi/qtgb7kglku85j76y50r3j/1.-Band-1-1648-233-245.pdf?rlkey=jfjgd5snndh43njt2gy16y5jl&st=lms3xw2u&raw=1"
page_number = st.number_input("Go to page:", min_value=1, value=1, step=1)

st.markdown(
    f'<a href="{pdf_url}#page={page_number}" target="_blank">Open PDF on page {page_number}</a>',
    unsafe_allow_html=True
)
