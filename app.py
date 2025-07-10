import streamlit as st
import pandas as pd
import tempfile
import os
from etl_main_cloud import generate_giva_format  # Adjust import if needed

# ---------------------- Custom CSS ----------------------
custom_css = """
<style>
body {
    font-family: "Segoe UI", sans-serif;
    background: linear-gradient(135deg, #e8f1fa, #ffffff);
    color: #1e3557;
}

h1 {
    color: #0072ff;
    text-align: center;
    margin-bottom: 0.5rem;
}

.stButton>button {
    background-color: #0072ff;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5em 1em;
    font-size: 16px;
    margin: 0.3rem;
    cursor: pointer;
    transition: background 0.3s;
}

.stButton>button:hover {
    background-color: #005bb5;
}

.upload-box {
    background-color: white;
    margin: 1rem auto;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    max-width: 650px;
}
.download-box button {
    background-color: #0072ff !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6em 1.2em !important;
    font-size: 16px !important;
    cursor: pointer !important;
    transition: background-color 0.3s ease !important;
}

.download-box button:hover {
    background-color: #005bb5 !important;
}
.dataframe {
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: auto;
    scrollbar-width: thin;
    scrollbar-color: #0072ff #e8f1fa;
    max-height: 500px;
}

/* Enhance tab titles */
.stTabs [role="tab"] {
    background-color: #f0f7ff;
    color: #0072ff;
    font-weight: 600;
    font-size: 16px;
    padding: 0.6rem 1rem;
    margin-right: 4px;
    border-radius: 10px 10px 0 0;
    transition: background-color 0.3s, color 0.3s;
}

.stTabs [aria-selected="true"] {
    background-color: #0072ff !important;
    color: white !important;
}

.stTextInput>div>div>input {
    border-radius: 8px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------- Session State ----------------------
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

st.markdown("<h1>💎 Giva PO Excel Generator 💎</h1>", unsafe_allow_html=True)
# ---------------------- Upload Box ----------------------
st.markdown('<div class="upload-box">', unsafe_allow_html=True)
uploaded = st.file_uploader("📥 **Giva PO Upload**", type=["xlsx", "xls"], key='uploader')
if uploaded:
    st.session_state.uploaded_file = uploaded
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------- Process & Preview ----------------------
if st.session_state.uploaded_file:
    uploaded_file = st.session_state.uploaded_file
    uploaded_file_name = os.path.splitext(uploaded_file.name)[0]
    output_filename = f"Output_{uploaded_file_name}.xlsx"
    output_path = os.path.join(tempfile.gettempdir(), output_filename)

    progress = st.progress(0, text="Starting process...")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_input:
            tmp_input.write(uploaded_file.read())
            input_path = tmp_input.name

        progress.progress(30, text="Running ETL...")
        generate_giva_format(input_path, output_path)

        progress.progress(70, text="Loading preview...")
        xls = pd.ExcelFile(output_path)
        progress.progress(100, text="✅ Done!")

        st.success("File processed successfully!")

        # Preview tabs
        st.markdown("### 📊 Preview Generated File")
        tab_titles = [f"📄 {sheet}" for sheet in xls.sheet_names]
        tabs = st.tabs(tab_titles)

        for tab, sheet in zip(tabs, xls.sheet_names):
            with tab:
                df_preview = pd.read_excel(xls, sheet_name=sheet)
                st.dataframe(df_preview, use_container_width=True, hide_index=True)

        # Download 
        


        st.markdown('''
<div style="
    background-color: blue;
    margin: 1rem auto;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    max-width: 650px;
    text-align: center;
    color: #0072ff;">
''', unsafe_allow_html=True)

        with open(output_path, "rb") as f:
            st.download_button(
                label=f"⬇️ Download {output_filename} ⬇️",
                data=f,
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )


    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.markdown(
        "<p style='text-align:center; color:#555;'>Upload a Giva PO Excel file to get started.</p>",
        unsafe_allow_html=True
    )

# ---------------------- Footer ----------------------
st.markdown("""
<br>
<div style="text-align:center; font-size: small; color: #0072ff;">
    Made By Afzal Asar & Ruchir Powar✨ | Ai Automation Team
</div>
""", unsafe_allow_html=True)
