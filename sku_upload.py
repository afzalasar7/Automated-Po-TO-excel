import streamlit as st
import psycopg2
import pandas as pd

# ---------- Database Function ----------
def insert_new_mapping(givadsgcd, auradsgcd, remarks=None, oldgivadsgcd=None):
    NEON_CONN_PARAMS = {
        'host': "ep-mute-grass-a138r2r4-pooler.ap-southeast-1.aws.neon.tech",
        'dbname': "neondb",
        'user': "neondb_owner",
        'password': "npg_O5yZTR4PeiHM",
        'sslmode': "require"
    }

    try:
        conn = psycopg2.connect(**NEON_CONN_PARAMS)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM public.giva_sku_mapping WHERE givadsgcd = %s", (givadsgcd,))
        if cursor.fetchone():
            st.markdown(
                f"<div style='color:#8a2be2;'>⚠️ Skipped duplicate: `{givadsgcd}` already exists.</div>",
                unsafe_allow_html=True
            )
            return

        insert_query = """
            INSERT INTO public.giva_sku_mapping (givadsgcd, auradsgcd, remarks, oldgivadsgcd)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (givadsgcd, auradsgcd, remarks, oldgivadsgcd))
        conn.commit()
        st.markdown(
            f"<div style='color:#6a5acd;'>✅ Inserted mapping: <b>{givadsgcd}</b> → <b>{auradsgcd}</b></div>",
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error(f"❌ Error inserting mapping: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

# ---------- Page Renderer ----------
def render():
    st.markdown("<h2>Add Giva Design Code and Aura Style Code:</h2>", unsafe_allow_html=True)

    st.markdown("""
    <table style="width:100%; border: 1px solid #ddd; border-collapse: collapse; margin-bottom: 1em;">
        <thead>
            <tr style="background-color: #6F42C1; color: white;">
                <th style="padding: 8px; border: 1px solid #ddd;">Giva Design Code</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Aura Style Code</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">GDLER0863</td>
                <td style="padding: 8px; border: 1px solid #ddd;">25GLE30011A0GL</td>
            </tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)

    # ---------- Tabs ----------
    tab1, tab2 = st.tabs(["📝 Manual Entry", "📋 Bulk Paste from Excel"])

    # ---------- Earring Code Set ----------
    earring_codes = {"LE", "GE", "TE", "NE", "NR", "PE"}

# ---------- Tab 1: Manual Entry ----------
    with tab1:
        if "sku_rows" not in st.session_state:
            st.session_state.sku_rows = 1

        input_data = []
        for i in range(st.session_state.sku_rows):
            cols = st.columns([6, 6])  # Giva | Aura
            with cols[0]:
                giva = st.text_input(f"Giva Design Code {i+1}", key=f"giva_{i}")
            with cols[1]:
                aura = st.text_input(f"Aura Style Code {i+1}", key=f"aura_{i}")

            # Auto-calculate remarks based on aura substring
            code_segment = aura[3:5].upper() if len(aura) >= 5 else ""
            remarks = "regular Chaki" if code_segment in earring_codes else None

            input_data.append((giva.strip(), aura.strip(), remarks))

                # Inject custom CSS for compact button style
        st.markdown("""
            <style>
            div.stButton > button {
                padding: 5px 8px;
                font-size: 10px;
                line-height: 1;
            }
            </style>
        """, unsafe_allow_html=True)

        # Render the button
        if st.button("➕ Add Another Row"):
            st.session_state.sku_rows += 1


        submit_cols = st.columns([1, 50, 1])
        with submit_cols[1]:
            submitted = st.button("✅ Submit All Mappings", use_container_width=True)
            if submitted:
                for giva, aura, remarks in input_data:
                    if giva and aura:
                        insert_new_mapping(giva, aura, remarks)
                    else:
                        st.markdown(
                            "<div style='color:#d2691e;'>⚠️ Please fill in both Giva and Aura codes before submitting.</div>",
                            unsafe_allow_html=True
                        )

    # ---------- Tab 2: Bulk Paste ----------
    with tab2:
        st.info("Paste your Excel data below. Format must match: `Giva Design Code`, `Aura Style Code`.")
        st.warning("Please Ensure You insert only the correct data in the correct format.")

        if "bulk_table_df" not in st.session_state or st.session_state.get("refresh_bulk_table", False):
            st.session_state.bulk_table_df = pd.DataFrame({
                "Giva Design Code": [""] * 100,
                "Aura Style Code": [""] * 100,
            })
            st.session_state.refresh_bulk_table = False

        edited_df = st.data_editor(
            st.session_state.bulk_table_df,
            num_rows="dynamic",
            use_container_width=True,
            key="editable_bulk_upload"
        )

        st.session_state.bulk_table_df = edited_df

        btn_cols = st.columns([5, 20, 13, 5])
        with btn_cols[1]:
            submit_bulk = st.button("🚀 Submit", use_container_width=True)
        with btn_cols[2]:
            if st.button("🔄 Refresh Table", use_container_width=True):
                st.session_state.refresh_bulk_table = True
                st.rerun()

        if submit_bulk:
            for i, row in edited_df.iterrows():
                giva = row["Giva Design Code"].strip()
                aura = row["Aura Style Code"].strip()
                code_segment = aura[3:5].upper() if len(aura) >= 5 else ""
                remarks = "regular Chaki" if code_segment in earring_codes else None

                if giva and aura:
                    insert_new_mapping(giva, aura, remarks)
                else:
                    continue  # skip incomplete rows
