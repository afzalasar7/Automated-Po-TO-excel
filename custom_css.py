def custom_css():
    return """
    <style>
    html, body, [class*="css"] {
        height: 100%;
        margin: 0;
        padding: 0;
        font-family: 'Segoe UI', Tahoma, sans-serif;
        background-color: #f2f4f8; /* ✅ Soft modern background */
        color: #333;
    }

    /* Layout Containers */
    .container, .upload-box {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        padding: 2rem;
        margin-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #6F42C1;
        text-align: center;
        margin-bottom: 1rem;
    }

    /* Buttons */
    .stButton>button {
        background-color: #6F42C1;
        color: white;
        font-size: 16px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        transition: 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #5a32a3;
    }

    /* Tabs */
    .stTabs [role="tab"] {
        background-color: #e6e0f3;
        color: #6F42C1;
        font-weight: 600;
        font-size: 16px;
        padding: 0.5rem 1rem;
        margin-right: 4px;
        border-radius: 8px 8px 0 0;
        transition: 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background-color: #6F42C1 !important;
        color: white !important;
    }

    /* Alerts & Notes */
    .element-container .stAlert {
        border-radius: 8px;
    }

    /* Tables */
    table {
        width: 100%;
        border-collapse: collapse;
    }

    th, td {
        border: 1px solid #ddd;
        padding: 10px;
        text-align: center;
    }

    thead {
        background-color: #6F42C1;
        color: white;
    }

    tbody tr:nth-child(even) {
        background-color: #f6f6f6;
    }

    /* Input Fields */
    input {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 4px;
        padding: 8px;
        font-size: 14px;
        width: 100%;
    }

    /* Footer */
    footer {
        background-color: #f0f0f0;
        padding: 12px;
        font-size: 0.85rem;
        text-align: center;
        color: #6F42C1;
        border-top: 1px solid #ccc;
        margin-top: 3rem;
    }
    </style>
    """
