import os
import pandas as pd
import requests
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from dotenv import load_dotenv
import numpy as np

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
    
    default_years = []
    default_columns = []
    # Prepare defaults, as saved
    db = st.session_state.firebase.database()
    users = db.child("users")
    email = st.session_state.email
    sanitized_email = email.replace(".", "_").replace("@", "_")
    # print(users)
    try:
        users.get.each()
    except:
        db.child("users").set({f"{sanitized_email}": {"years": None, "selected_columns": None}})
    
    response1 = db.child("users").child(sanitized_email).child("years").get().val()
    if response1:
        st.session_state.default_years = response1
    response2 = db.child("users").child(sanitized_email).child("selected_columns").get().val()
    if response2:
        st.session_state.default_columns = response2
    # User input for year
    years = st.multiselect("Select the years for the data:", [2025, 2024, 2023, 2022, 2021], default=st.session_state.default_years)
    cids = {
        "2025": os.getenv("FE_2025"),
        "2024": os.getenv("FE_2024"),
        "2023": os.getenv("FE_2023"),
        "2022": os.getenv("FE_2022"),
        "2021": os.getenv("FE_2021")
    }

    # Fetch and visualize data
    cids_chosen = []
    db.child("users").child(sanitized_email).update({"years":years})
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
                default=st.session_state.default_columns
            )
            db.child("users").child(sanitized_email).update({"selected_columns":selected_columns})
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
    
     # User input for year
    year = st.selectbox("Select the year for the data:", [2025, 2024, 2023, 2022, 2021])
    cids = {
        "2025": os.getenv("FE_2025"),
        "2024": os.getenv("FE_2024"),
        "2023": os.getenv("FE_2023"),
        "2022": os.getenv("FE_2022"),
        "2021": os.getenv("FE_2021")
    }

    # Fetch and visualize data
    cid = cids.get(str(year))
    if not cid:
        st.error("No data available for the selected year.")
        return

    df = get_data_for_year(cid)
    if df is not None:
        visualize_data(df)

# Added in
# Function to visualize the data
def visualize_data(df):
    st.subheader("Fuel Efficiency and Environmental Impact Analysis")

    # Remove outliers in fuel efficiency
    df_filtered = df[(df['Comb FE (Guide) - Conventional Fuel'] >= 20) & (df['Comb FE (Guide) - Conventional Fuel'] <= 60)]

    # Top N carlines by fuel efficiency
    top_n = 10
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
    st.write(
        "This bar chart highlights the top 10 Toyota carlines based on their average fuel efficiency. "
        "It helps identify the carlines that perform best in terms of fuel economy, which is crucial for cost-saving "
        "and environmental considerations. Higher fuel efficiency means less fuel consumption and lower carbon emissions."
    )

    # Advanced Filtering
    st.sidebar.header("Advanced Filters")
    selected_carline = st.sidebar.multiselect("Select Carlines:", options=df['Carline'].unique())
    min_fe, max_fe = st.sidebar.slider(
        "Select Fuel Efficiency Range (MPG):", 
        min_value=int(df_filtered['Comb FE (Guide) - Conventional Fuel'].min()), 
        max_value=int(df_filtered['Comb FE (Guide) - Conventional Fuel'].max()), 
        value=(20, 60)
    )
    
    df_filtered = df_filtered[ 
        (df_filtered['Comb FE (Guide) - Conventional Fuel'] >= min_fe) & 
        (df_filtered['Comb FE (Guide) - Conventional Fuel'] <= max_fe)
    ]
    if selected_carline:
        df_filtered = df_filtered[df_filtered['Carline'].isin(selected_carline)]

    # Summary Statistics
    st.write("### Summary Statistics")
    st.write(f"**Average Fuel Efficiency:** {df_filtered['Comb FE (Guide) - Conventional Fuel'].mean():.2f} MPG")
    st.write(f"**Median Fuel Efficiency:** {df_filtered['Comb FE (Guide) - Conventional Fuel'].median():.2f} MPG")
    st.write(f"**Fuel Efficiency Standard Deviation:** {df_filtered['Comb FE (Guide) - Conventional Fuel'].std():.2f} MPG")

    # Scatter Plot: Fuel Efficiency vs Engine Displacement
    if 'Eng Displ' in df.columns:
        st.write("### Fuel Efficiency vs Engine Displacement")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(x=df_filtered['Eng Displ'], y=df_filtered['Comb FE (Guide) - Conventional Fuel'], ax=ax, color='blue')
        ax.set_title("Fuel Efficiency vs Engine Displacement")
        ax.set_xlabel("Engine Displacement (L)")
        ax.set_ylabel("Fuel Efficiency (MPG)")
        st.pyplot(fig)
        st.write(
            "This scatter plot demonstrates how engine displacement (in liters) influences fuel efficiency. "
            "In general, larger engines tend to have lower fuel efficiency, but this plot allows for a more detailed "
            "comparison of different carlines. Understanding this relationship helps buyers make informed decisions about fuel economy."
        )

    # CO2 Emissions by Carline: City and Highway CO2
    if 'City CO2 Rounded Adjusted' in df.columns and 'Hwy CO2 Rounded Adjusted' in df.columns:
        st.write("### CO2 Emissions (City vs Highway) by Carline")

        # Dropdown for selecting specific carlines
        available_carlines = df['Carline'].unique()
        selected_carlines = st.multiselect("Select carlines to compare:", available_carlines, default=available_carlines[:5])

        if selected_carlines:
            # Filter data for selected carlines
            df_selected = df[df['Carline'].isin(selected_carlines)]

            df_co2 = df_selected.groupby('Carline').agg({
                'City CO2 Rounded Adjusted': 'mean',
                'Hwy CO2 Rounded Adjusted': 'mean'
            }).sort_values('City CO2 Rounded Adjusted', ascending=True)

            fig, ax = plt.subplots(figsize=(10, 6))
            df_co2.plot(kind='bar', ax=ax, color=['green', 'blue'])
            ax.set_title(f"CO2 Emissions by Carline (City vs Highway)")
            ax.set_ylabel("CO2 Emissions (g/mile)")
            ax.set_xlabel("Carline")
            st.pyplot(fig)
            st.write(
                "This bar chart compares the average CO2 emissions for selected Toyota carlines in both city and highway driving. "
                "It illustrates how different carlines impact the environment, with city driving typically generating more emissions "
                "due to lower efficiency in stop-and-go traffic. By comparing emissions across carlines, users can identify the more eco-friendly options."
            )

    # User Column Selection for Custom Chart
    st.sidebar.header("Custom Chart Selection")
    available_columns = df.columns.tolist()

    # Ensure required columns for plotting are available
    available_columns = [col for col in available_columns if col != 'Mfr Name']

    x_column = st.sidebar.selectbox("Select the X-axis column for the plot:", available_columns)
    y_column = st.sidebar.selectbox("Select the Y-axis column for the plot:", available_columns)

    if x_column and y_column:
        st.write(f"### {x_column} vs {y_column}")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(x=df_filtered[x_column], y=df_filtered[y_column], ax=ax, color='purple')
        ax.set_title(f"{x_column} vs {y_column}")
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
        st.pyplot(fig)

    # Data Download Option
    st.sidebar.download_button(
        "Download Filtered Data as CSV",
        df_filtered.to_csv(index=False),
        "filtered_toyota_data.csv",
        "text/csv"
    )


# Run the Streamlit app
if __name__ == "__main__":
    main()
