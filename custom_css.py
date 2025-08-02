# custom_css.py

def custom_css():
    return """
    <style>
    html, body, [class*="css"] {
        height: 100%;
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
        background-color: #f5f5f5;
    }

    .container {
        max-width: 800px;
        margin: 0 auto;
        padding: 40px;
    }

    h1 {
        font-size: 36px;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 1rem;
    }

    .upload-box {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        padding: 2rem;
        margin-bottom: 2rem;
    }

    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 0.75em 1.5em;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.3s;
    }

    .stButton>button:hover {
        background-color: #45a049;
    }

    .download-box button {
        background-color: #4CAF50 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75em 1.5em !important;
        font-size: 16px !important;
        cursor: pointer !important;
    }

    .stTabs [role="tab"] {
        background-color: #ffffff;
        color: #4CAF50;
        font-weight: 600;
        font-size: 16px;
        padding: 0.6rem 1rem;
        margin-right: 4px;
        border-radius: 10px 10px 0 0;
        transition: background-color 0.3s, color 0.3s;
    }

    .stTabs [aria-selected="true"] {
        background-color: #4CAF50 !important;
        color: white !important;
    }

    footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: #f5f5f5;
        padding: 10px;
        text-align: center;
        font-size: small;
        color: #4CAF50;
    }
    </style>
    """
