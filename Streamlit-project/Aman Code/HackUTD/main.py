import os
import pandas as pd
import requests
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from dotenv import load_dotenv
from methods import process_fuel_efficient_car  # Assuming you have this function for predictions

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

            # Print column names for debugging
            st.write("Columns in the dataset:", df.columns.tolist())

            # Ensure 'Mfr Name' is string type (only if it's not already)
            df['Mfr Name'] = df['Mfr Name'].astype(str)

            # Check if required columns exist (excluding 'Curb Weight')
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

# Function to visualize the data
def visualize_data(df):
    st.subheader("Fuel Efficiency and Environmental Impact Analysis")

    # Remove outliers in fuel efficiency
    df_filtered = df[(df['Comb FE (Guide) - Conventional Fuel'] >= 20) & (df['Comb FE (Guide) - Conventional Fuel'] <= 60)]

    # Top N carlines by fuel efficiency
    top_n = 10  # You can adjust this number
    Carline_avg_fe = df_filtered.groupby('Carline')['Comb FE (Guide) - Conventional Fuel'].mean().sort_values(ascending=False).head(top_n)
    
    if Carline_avg_fe.empty:
        st.warning("No data available for the top models.")
        return

    # Bar Chart: Top N Carlines by Average Fuel Efficiency
    st.write(f"### Top {top_n} Carlines by Average Fuel Efficiency (MPG)")
    fig, ax = plt.subplots(figsize=(10, 6))
    Carline_avg_fe.plot(kind='bar', ax=ax, color='orange')
    ax.set_title(f"Top {top_n} Carlines by Average Fuel Efficiency (MPG)")
    ax.set_ylabel("Average MPG")
    ax.set_xlabel("Carline")
    st.pyplot(fig)

    # Add Summary for Bar Graph: Top Carlines by Fuel Efficiency
    st.markdown("""
    <div class="summary">
        <h4>Top 10 Carlines by Average Fuel Efficiency (MPG)</h4>
        <p>This chart displays the top 10 Toyota carlines based on their combined fuel efficiency. 
        Higher fuel efficiency means lower fuel consumption, which can help you save money on fuel and reduce environmental impact.</p>
        <p>The Toyota carlines with the highest fuel efficiency in this dataset are leading in terms of sustainability and cost-effectiveness.</p>
    </div>
    """, unsafe_allow_html=True)

    # Scatter Plot: Fuel Efficiency vs Engine Displacement
    if 'Eng Displ' in df.columns:
        st.write("### Fuel Efficiency vs Engine Displacement")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(x=df_filtered['Eng Displ'], y=df_filtered['Comb FE (Guide) - Conventional Fuel'], ax=ax, color='blue')
        ax.set_title("Fuel Efficiency vs Engine Displacement")
        ax.set_xlabel("Engine Displacement (L)")
        ax.set_ylabel("Fuel Efficiency (MPG)")
        st.pyplot(fig)

        # Add Summary for Scatter Plot: Fuel Efficiency vs Engine Displacement
        st.markdown("""
        <div class="summary">
            <h4>Fuel Efficiency vs Engine Displacement</h4>
            <p>This scatter plot shows the relationship between engine displacement and fuel efficiency. Typically, larger engines consume more fuel, which reduces fuel efficiency. 
            Smaller engines tend to have better fuel efficiency but may impact vehicle performance in certain conditions.</p>
            <p>Choosing a Toyota with an efficient engine size can provide the perfect balance of performance and fuel savings.</p>
        </div>
        """, unsafe_allow_html=True)

    # CO2 Emissions by Carline: City and Highway CO2
    if 'City CO2 Rounded Adjusted' in df.columns and 'Hwy CO2 Rounded Adjusted' in df.columns:
        st.write("### CO2 Emissions (City vs Highway) by Carline")
        df_co2 = df_filtered.groupby('Carline').agg({
            'City CO2 Rounded Adjusted': 'mean',
            'Hwy CO2 Rounded Adjusted': 'mean'
        }).sort_values('City CO2 Rounded Adjusted', ascending=True).head(top_n)

        fig, ax = plt.subplots(figsize=(10, 6))
        df_co2.plot(kind='bar', ax=ax, color=['green', 'blue'])
        ax.set_title(f"CO2 Emissions by Carline (Top {top_n})")
        ax.set_ylabel("CO2 Emissions (g/mile)")
        ax.set_xlabel("Carline")
        st.pyplot(fig)

        # Add Summary for CO2 Emissions Comparison
        st.markdown("""
        <div class="summary">
            <h4>CO2 Emissions Comparison (City vs Highway)</h4>
            <p>This bar chart compares the CO2 emissions for city and highway driving by carline. 
            Lower CO2 emissions indicate a more environmentally friendly vehicle, which contributes to cleaner air quality and lower environmental impact.</p>
            <p>Choosing a Toyota carline with lower emissions for both city and highway driving helps reduce your carbon footprint while providing better fuel economy.</p>
        </div>
        """, unsafe_allow_html=True)

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

    # User input for year
    year = st.selectbox("Select the year for the data:", [2025,2024, 2023, 2022, 2021])
    cids = {
        "2025": os.getenv("FE_2025"),
        "2024": os.getenv("FE_2024"),
        "2023": os.getenv("FE_2023"),
        "2022": os.getenv("FE_2022"),
        "2021": os.getenv("FE_2021")
    }

    # Fetch and visualize data
    cid = cids.get(str(year))
    if cid:
        df = get_data_for_year(cid)
        if df is not None:
            visualize_data(df)
    else:
        st.error("Data for the selected year is not available.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
