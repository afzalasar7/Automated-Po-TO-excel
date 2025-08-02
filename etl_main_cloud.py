import pandas as pd
import numpy as np
import psycopg2
import os
import math

# -------------------- Helper Functions --------------------

def calculate_weight_range(weight_in_grams):
    try:
        val = float(weight_in_grams)
    except (TypeError, ValueError):
        return [np.nan, np.nan]
    
    if val <= 2:
        tolerance_mg = 150
    elif val <= 4:
        tolerance_mg = 200
    else:
        tolerance_mg = 250

    tolerance_g = tolerance_mg / 1000.0
    min_weight = val - tolerance_g
    max_weight = val + tolerance_g

    min_rounded = math.floor(round(min_weight, 3) * 100) / 100
    max_rounded = math.floor(round(max_weight, 3) * 100) / 100

    return [min_rounded, max_rounded]

def remark(row):
    try:
        gross = float(row['Gross Wt.'])
        net = float(row['Gold wt'])
        gross_min, gross_max = calculate_weight_range(gross)
        net_min, net_max = calculate_weight_range(net)

        return (
            f"VERY VERY URGENT, PER PCS "
            f"(GROSS WT- MIN {gross_min}-{gross_max} MAX), "
            f"(NET WT- MIN {net_min}-{net_max} MAX)"
        )
    except:
        return ''

def get_tone(color):
    if isinstance(color, str):
        color = color.lower()
        if 'rose' in color or 'pink' in color:
            return 'P'
        elif 'yellow' in color:
            return 'Y'
        elif 'white' in color:
            return 'W'
    return 'Y'

def build_sheet(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    df['SrNo'] = np.arange(1, len(df) + 1)
    df['OrderQty'] = df['Quantity']
    df['OrderItemPcs'] = df['Quantity']
    df['ItemSize'] = df['GivaDsgCd'].astype(str).apply(lambda x: "12" if x.startswith("GDLR") else "")
    df['Metal'] = df['Gold purity'].apply(lambda x: 'GA14' if '14' in str(x) else 'GA18')
    df['Tone'] = df['Gold Color'].apply(get_tone)
    df['ItemPoNo'] = ''
    df['ItemRefNo'] = ''
    df['StockType'] = ''
    df['MakeType'] = ''
    df['CustomerProductionInstruction'] = 'DIA QUALITY : BELOW 0.20 PTR HPHTVVSVSGH & ABOVE 0.20 PTR CVD VVS VS GH'
    df['SpecialRemarks'] = df.apply(remark, axis=1)
    df['DesignProductionInstruction'] = ''
    df['StampInstruction'] = df['Metal'].apply(
        lambda x: 'BIS LOGO, 14K585, HUID NO.' if x == 'GA14' else 'BIS LOGO, 18K750, HUID NO.'
    )
    df['OrderGroup'] = df['GivaDsgCd']
    df['Certificate'] = ''
    df['Basemetalminwt'], df['Basemetalmaxwt'] = zip(*df['Gold wt'].map(calculate_weight_range))
    df['Basestoneminwt'] = ''
    df['Basestonemaxwt'] = ''
    df['Productiondeliverydate'] = ''
    df['Expecteddeliverydate'] = ''
    df['SetPrice'] = ''
    df['StoneQuality'] = ''
    df['StyleCode'] = df['AuraDsgCd']

    final_cols = [
        'SrNo', 'StyleCode', 'ItemSize', 'OrderQty', 'OrderItemPcs',
        'Metal', 'Tone', 'ItemPoNo', 'ItemRefNo', 'StockType', 'MakeType',
        'CustomerProductionInstruction', 'SpecialRemarks', 'DesignProductionInstruction',
        'StampInstruction', 'OrderGroup', 'Certificate', 'SKUNo',
        'Basestoneminwt', 'Basestonemaxwt', 'Basemetalminwt', 'Basemetalmaxwt',
        'Productiondeliverydate', 'Expecteddeliverydate', 'SetPrice', 'StoneQuality'
    ]

    df = df.loc[:, ~df.columns.duplicated()]
    return df.reindex(columns=final_cols)

# -------------------- Main ETL Function --------------------

def generate_giva_format(po_file, output_file):
    preview = pd.read_excel(po_file, nrows=20, header=None)
    expected_column = "SKU"
    start_row = next(
        (i for i, row in preview.iterrows() if row.astype(str).str.strip().str.contains(expected_column).any()), 
        0
    )

    df_po = pd.read_excel(po_file, skiprows=start_row, header=None)
    df_po.columns = df_po.iloc[0].astype(str).str.strip()
    df_po = df_po[1:].reset_index(drop=True)
    df_po = df_po[df_po['SKU'].notna()].rename(columns={'SKU': 'GivaDsgCd'})

    # Neon DB connection
    NEON_CONN_PARAMS = {
        'host': "ep-mute-grass-a138r2r4-pooler.ap-southeast-1.aws.neon.tech",
        'dbname': "neondb",
        'user': "neondb_owner",
        'password': "npg_O5yZTR4PeiHM",
        'sslmode': "require"
    }
    try:
        conn = psycopg2.connect(**NEON_CONN_PARAMS)
        print("✅ Connected to Neon PostgreSQL")
        df_mapping = pd.read_sql("SELECT * FROM public.giva_sku_mapping", conn)
        print("df_mapping columns:", df_mapping.columns.tolist())

        conn.close()
    except Exception as e:
        print("❌ Neon DB connection failed:", e)
        return
    df_mapping = df_mapping.rename(columns={'givadsgcd': 'GivaDsgCd', 'auradsgcd': 'AuraDsgCd', 'oldgivadsgcd': 'OldGivaDsgCd'})

    df_merged = pd.merge(df_po, df_mapping[['GivaDsgCd', 'AuraDsgCd']], on='GivaDsgCd', how='left')

    unmatched = df_merged[df_merged['AuraDsgCd'].isnull()]
    if not unmatched.empty and 'OldGivaDsgCd' in df_mapping.columns:
        mapping_old = df_mapping[['OldGivaDsgCd', 'AuraDsgCd']].dropna().rename(columns={'OldGivaDsgCd': 'GivaDsgCd'})
        unmatched = pd.merge(unmatched.drop(columns=['AuraDsgCd']), mapping_old, on='GivaDsgCd', how='left')

    df_final = pd.concat([
        df_merged[df_merged['AuraDsgCd'].notnull()],
        unmatched
    ], ignore_index=True)

    df_14k = df_final[df_final['Gold purity'].astype(str).str.contains('14', na=False)]
    df_18k = df_final[df_final['Gold purity'].astype(str).str.contains('18', na=False)]

    sheet_14k = build_sheet(df_14k) if not df_14k.empty else None
    sheet_18k = build_sheet(df_18k) if not df_18k.empty else None

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        if sheet_14k is not None:
            sheet_14k.to_excel(writer, index=False, sheet_name='14K')
        if sheet_18k is not None:
            sheet_18k.to_excel(writer, index=False, sheet_name='18K')

    print(f"✅ GIVA Excel generated at: {output_file}")

import psycopg2

import psycopg2

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

        # Check for existing givadsgcd
        cursor.execute("SELECT 1 FROM public.giva_sku_mapping WHERE givadsgcd = %s", (givadsgcd,))
        if cursor.fetchone():
            print(f"⚠️ Duplicate entry skipped: {givadsgcd} already exists.")
            return

        # Insert if not duplicate
        insert_query = """
            INSERT INTO public.giva_sku_mapping (givadsgcd, auradsgcd, remarks, oldgivadsgcd)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (givadsgcd, auradsgcd, remarks, oldgivadsgcd))
        conn.commit()
        print(f"✅ Inserted mapping: {givadsgcd} → {auradsgcd}")

    except Exception as e:
        print(f"❌ Failed to insert mapping: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

insert_new_mapping("GDLER0863", "25GLE30011A0GL", "", "")
import psycopg2

def delete_duplicate_mappings():
    NEON_CONN_PARAMS = {
        'host': "ep-mute-grass-a138r2r4-pooler.ap-southeast-1.aws.neon.tech",
        'dbname': "neondb",
        'user': "neondb_owner",
        'password': "npg_O5yZTR4PeiHM",
        'sslmode': "require"
    }

    delete_query = """
    DELETE FROM public.giva_sku_mapping a
    USING public.giva_sku_mapping b
    WHERE 
        a.ctid > b.ctid AND  -- keep first occurrence
        a.givadsgcd = b.givadsgcd AND
        a.auradsgcd = b.auradsgcd
    """

    try:
        conn = psycopg2.connect(**NEON_CONN_PARAMS)
        cursor = conn.cursor()
        cursor.execute(delete_query)
        deleted_count = cursor.rowcount
        conn.commit()
        print(f"✅ Deleted {deleted_count} duplicate rows based on givadsgcd + auradsgcd.")
    except Exception as e:
        print(f"❌ Failed to delete duplicates: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
delete_duplicate_mappings()