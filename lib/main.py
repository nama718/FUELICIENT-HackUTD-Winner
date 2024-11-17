import os
import pandas as pd
import requests
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to fetch data from IPFS using CID
def get_data_from_ipfs(cid):
    """Fetch the data from IPFS using the provided CID."""
    url = f"https://gateway.pinata.cloud/ipfs/{cid}"
    try:
        response = requests.get(url)

        if response.status_code == 200:
            # Return the content as bytes to read it into pandas
            return BytesIO(response.content)
        else:
            st.error(f"Failed to fetch data for CID {cid}. Status Code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Function to get and process the data from a dataset CID
def get_data_for_year(cid):
    """Fetch the data for a given year and filter for Toyota cars based on 'Mfr Name'."""
    data = get_data_from_ipfs(cid)

    if data:
        try:
            # Read the dataset into pandas DataFrame
            df = pd.read_excel(data)

            # Clean up column names and data
            df.columns = df.columns.str.strip()  # Strip spaces from column names
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)  # Strip spaces from object type columns

            # Ensure 'Mfr Name' is string type (only if it's not already)
            df['Mfr Name'] = df['Mfr Name'].astype(str)

            # Check if required columns exist
            required_columns = ['Mfr Name', 'Carline', 'Comb FE (Guide) - Conventional Fuel', 'Eng Displ', 'City CO2 Rounded Adjusted', 'Hwy CO2 Rounded Adjusted']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Error: Missing the following required columns: {', '.join(missing_columns)}")
                return None

            # Drop rows where key columns are NaN
            df = df.dropna(subset=['Mfr Name', 'Carline', 'Comb FE (Guide) - Conventional Fuel', 'Eng Displ'])

            # Filter Toyota cars
            df_toyota = df[df['Mfr Name'].str.contains('TOYOTA', case=False, na=False)]

            if df_toyota.empty:
                st.warning(f"No Toyota cars found in the data for CID {cid}.")
                return None

            return df_toyota

        except Exception as e:
            st.error(f"Error processing data: {e}")
            return None
    return None

# Function to visualize the selected columns
def visualize_selected_columns(df, selected_columns):
    st.markdown("---")
    st.markdown(f"## Visualizing Selected Columns:")
    st.write(f"{', '.join(selected_columns)}")

    # Ensure the columns are available in the dataframe
    if all(col in df.columns for col in selected_columns):
        # Ensure columns are numeric
        if not all(pd.api.types.is_numeric_dtype(df[col]) for col in selected_columns):
            st.error("All selected columns must be numeric to generate a visualization.")
            return

        # If only two columns are selected, generate a scatter plot
        if len(selected_columns) == 2:
            col1, col2 = selected_columns
            st.write(f"#### Scatter Plot of {col1} vs {col2}")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.scatterplot(x=df[col1], y=df[col2], ax=ax)
            ax.set_title(f"{col1} vs {col2}")
            ax.set_xlabel(col1)
            ax.set_ylabel(col2)
            st.pyplot(fig)

        # If more than two columns are selected, create a bar chart for comparison
        else:
            st.write(f"#### Bar Chart of {', '.join(selected_columns)}")
            df_selected = df[selected_columns].mean().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(10, 6))
            df_selected.plot(kind='bar', ax=ax, color='orange')
            ax.set_title(f"Comparison of {', '.join(selected_columns)}")
            ax.set_ylabel("Average Value")
            ax.set_xlabel("Columns")
            st.pyplot(fig)

        # Add summaries based on selection
        st.markdown("""
        <div class="summary">
            <h4>Selected Column Comparison</h4>
            <p>This visualization allows you to compare the selected characteristics. 
            Use a scatter plot to visualize the relationship between two characteristics, or a bar chart to see how different characteristics perform on average.</p>
            <p>Experiment with different selections of characteristics. You might uncover something interesting about Toyota vehicles!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error(f"One or more of the selected columns are missing from the data: {', '.join(selected_columns)}")

# Main function to interact with Streamlit interface
def main():
    # App Title
    st.title("Toyota Fuel Efficiency and Environmental Impact Visualization")

    # Custom CSS for styling
    st.markdown("""
        <style>
            .stApp {
                background-color: #f4f7fa;
            }
            .css-1d391kg {
                text-align: center;
                font-size: 3rem;
                font-family: 'Arial', sans-serif;
                color: #1e1e1e;
            }
            .st-subheader {
                font-size: 1.5rem;
                font-family: 'Arial', sans-serif;
                color: #1e1e1e;
                margin-bottom: 20px;
            }
            .stTitle {
                text-align: center;
                font-size: 2.5rem;
                font-weight: bold;
                color: #2C3E50;
            }
            .stButton>button {
                background-color: #2980B9;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 5px;
            }
            .stButton>button:hover {
                background-color: #1A5276;
            }
            .css-1v3fvcr {
                margin-top: 10px;
            }
            .summary {
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                margin-top: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            .summary h4 {
                color: #2980B9;
                font-size: 1.3rem;
            }
            .summary p {
                color: #333333;
                font-size: 1.1rem;
                line-height: 1.6;
            }
        </style>
    """, unsafe_allow_html=True)
    
    db = st.session_state.firebase.database()
    
    # User input for year
    years = st.multiselect("Select the years for the data:", [2025, 2024, 2023, 2022, 2021])
    cids = {
        "2025": os.getenv("FE_2025"),
        "2024": os.getenv("FE_2024"),
        "2023": os.getenv("FE_2023"),
        "2022": os.getenv("FE_2022"),
        "2021": os.getenv("FE_2021")
    }

    # Fetch and visualize data
    cids_chosen = []
    for year in years:
        cids_chosen.append(cids.get(str(year)))
    if len(cids_chosen) > 0:
        dataframes = []
        for content_id in cids_chosen:
            if "cid_map" not in st.session_state:
                st.session_state.cid_map = {"":""}
            if content_id not in st.session_state.cid_map:
                print(f"Requesting data for cid {content_id}")
                st.session_state.cid_map[content_id] = get_data_for_year(content_id)
            current_df = st.session_state.cid_map[content_id]
            if current_df is not None:
                dataframes.append(current_df)
            else:
                st.error("Year data request failed")
        if len(dataframes) > 0:
            df = pd.concat(dataframes)
            # Allow users to select columns
            available_columns = df.columns.tolist()
            selected_columns = st.multiselect(
                "Select the columns you want to compare:",
                options=available_columns,
                default=['Model Year', 'Comb FE (Guide) - Conventional Fuel']
            )

            # Visualize the selected columns
            if selected_columns:
                visualize_selected_columns(df, selected_columns)
            else:
                st.warning("Please select at least two columns to compare.")
        else:
            st.error("No data available for the selected year.")
    else:
        if len(cids_chosen) > 0:
            st.error("Data for the selected year is not available.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
