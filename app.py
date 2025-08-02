import streamlit as st
from streamlit_option_menu import option_menu
from custom_css import custom_css
import sku_upload  # Custom page
import pandas as pd
import tempfile
import os
from etl_main_cloud import generate_giva_format  # Your ETL function

# ---------------------- Apply Custom CSS ----------------------
st.markdown(custom_css(), unsafe_allow_html=True)

# ---------------------- Title & Navigation ----------------------

selected = option_menu(
    menu_title=None,
    options=["Giva PO Generator", "Add New SKU"],
    icons=["filetype-xlsx", "database-add"],
    orientation="horizontal",
    default_index=0,
    styles = {
    "container": {
        "padding": "10px 20px",  # Added padding
    },
    "icon": {
        "font-size": "18px"
    },
    "nav-link": {
        "font-size": "18px",
        "text-align": "center",
        "margin": "0px",
        "--hover-color": "#e0e0e0"
    },
    "nav-link-selected": {
        "background-color": "#6F42C1",  # Indigo color
        "color": "white"
    },
}

    
)

# ---------------------- Route Logic ----------------------
if selected == "Giva PO Generator":
    # ---------------------- Upload Section ----------------------
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None

    st.markdown("<h1>💎 Giva PO Excel Generator</h1>", unsafe_allow_html=True)
    uploaded = st.file_uploader("📥 **Upload Giva PO File**", type=["xlsx", "xls"], key='uploader')
    if uploaded:
        st.session_state.uploaded_file = uploaded
    st.markdown('</div>', unsafe_allow_html=True)

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

            st.success("✅ File processed successfully!")

            st.markdown("### 📊 Preview of Generated File")
            tab_titles = [f"📄 {sheet}" for sheet in xls.sheet_names]
            tabs = st.tabs(tab_titles)

            for tab, sheet in zip(tabs, xls.sheet_names):
                with tab:
                    df_preview = pd.read_excel(xls, sheet_name=sheet)
                    st.dataframe(df_preview, use_container_width=True, hide_index=True)

            st.markdown('<div class="download-box">', unsafe_allow_html=True)
            with open(output_path, "rb") as f:
                st.download_button(
                    label=f"⬇️ Download {output_filename}",
                    data=f,
                    file_name=output_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error: {e}")
    else:
        st.markdown(
            "<p style='text-align:center; color:#666;'>Upload a Giva PO Excel file to begin processing.</p>",
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Add New SKU":
    sku_upload.render()  # Call function from sku_upload.py

# ---------------------- Footer ----------------------
st.markdown("""
<footer>
    Made by Afzal Asar & Ruchir Powar ✨ | AI Automation Team
</footer>
""", unsafe_allow_html=True)
