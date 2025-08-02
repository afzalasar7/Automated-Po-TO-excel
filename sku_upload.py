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
    st.markdown("<h2>🆕 Add Giva Design Code and Aura Style Code:</h2>", unsafe_allow_html=True)

    st.markdown("""
    <table style="width:100%; border: 1px solid #ddd; border-collapse: collapse; margin-bottom: 1em;">
        <thead>
            <tr style="background-color: #6F42C1; color: white;">
                <th style="padding: 8px; border: 1px solid #ddd;">Giva Design Code</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Aura Style Code</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Remarks (Is Earring?)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">GDLER0863</td>
                <td style="padding: 8px; border: 1px solid #ddd;">25GLE30011A0GL</td>
                <td style="padding: 8px; border: 1px solid #ddd;">Yes / No</td>
            </tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)

    # ---------- Tabs ----------
    tab1, tab2 = st.tabs(["📝 Manual Entry", "📋 Bulk Paste from Excel"])

    # ---------- Tab 1: Manual Entry ----------
    with tab1:
        if "sku_rows" not in st.session_state:
            st.session_state.sku_rows = 1

        input_data = []
        for i in range(st.session_state.sku_rows):
            cols = st.columns([4, 4, 4])  # Giva | Aura | Remarks
            with cols[0]:
                giva = st.text_input(f"Giva Code {i+1}", key=f"giva_{i}")
            with cols[1]:
                aura = st.text_input(f"Aura Code {i+1}", key=f"aura_{i}")
            with cols[2]:
                st.markdown('<div style="margin-bottom: 6px;"><b>Remarks (Is Earring?)</b></div>', unsafe_allow_html=True)
                is_earring = st.checkbox(" ", key=f"earring_{i}", label_visibility="collapsed")

            input_data.append((giva.strip(), aura.strip(), "regular Chaki" if is_earring else None))

        if st.button("➕ Add Another Row"):
            st.session_state.sku_rows += 1

        submit_cols = st.columns([1, 6, 1])
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
        st.info("Paste your Excel data below. Format must match: `givadsgcd`, `auradsgcd`, and `remarks (is earring)`.")

        # Template for editable table
        template_df = pd.DataFrame({
            "givadsgcd": [""],
            "auradsgcd": [""],
            "remarks (is earring)": [False]
        })

        edited_df = st.data_editor(
            template_df,
            num_rows="dynamic",
            use_container_width=True,
            key="editable_bulk_upload"
        )

        submit_bulk = st.button("🚀 Submit Bulk Mappings", use_container_width=True)
        if submit_bulk:
            for i, row in edited_df.iterrows():
                giva = row["givadsgcd"].strip()
                aura = row["auradsgcd"].strip()
                remarks = "regular Chaki" if row["remarks (is earring)"] else None

                if giva and aura:
                    insert_new_mapping(giva, aura, remarks)
                else:
                    st.markdown(
                        f"<div style='color:#d2691e;'>⚠️ Row {i+1}: Giva or Aura code is empty. Skipped.</div>",
                        unsafe_allow_html=True
                    )
