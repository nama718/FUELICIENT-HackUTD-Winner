import requests
import pandas as pd
from io import BytesIO
import streamlit as st

def get_data_from_ipfs(cid):
    """Fetch the data from IPFS using the provided CID."""
    url = f"https://gateway.pinata.cloud/ipfs/{cid}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            st.error(f"Failed to fetch data for CID {cid}. Status Code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def process_data(df):
    """Process and clean the data."""
    # Strip spaces from column names
    df.columns = df.columns.str.strip()

    # Strip spaces from object columns
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # Ensure 'Mfr Name' is string type
    df['Mfr Name'] = df['Mfr Name'].astype(str)

    # Check for required columns
    required_columns = ['Mfr Name', 'Carline', 'Comb FE (Guide) - Conventional Fuel', 'Eng Displ', 'City CO2 Rounded Adjusted', 'Hwy CO2 Rounded Adjusted']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"Error: Missing the following required columns: {', '.join(missing_columns)}")
        return None

    # Drop rows where critical columns are NaN
    df = df.dropna(subset=['Mfr Name', 'Carline', 'Comb FE (Guide) - Conventional Fuel', 'Eng Displ'])

    # Filter Toyota cars
    df_toyota = df[df['Mfr Name'].str.contains('TOYOTA', case=False, na=False)]

    if df_toyota.empty:
        st.warning("No Toyota cars found in the data.")
        return None

    return df_toyota

def get_data_for_year(cid):
    """Fetch and process data for the selected year."""
    data = get_data_from_ipfs(cid)
    if data:
        df = pd.read_excel(data)
        return process_data(df)
    return None
