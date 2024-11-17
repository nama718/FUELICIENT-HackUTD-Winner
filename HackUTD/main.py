import os
import pandas as pd
from dotenv import load_dotenv
import requests
from io import BytesIO
from methods import process_fuel_efficient_car

# Load environment variables from .env file
load_dotenv()

# Function to fetch data from Pinata using CID
def get_data_from_ipfs(cid):
    """Fetch the data from IPFS using the provided CID."""
    url = f"https://gateway.pinata.cloud/ipfs/{cid}"
    try:
        response = requests.get(url)

        if response.status_code == 200:
            # Return the content as bytes to read it into pandas
            return BytesIO(response.content)
        else:
            print(f"Failed to fetch data for CID {cid}. Status Code: {response.status_code}")
            print(f"Response Message: {response.text}")  # Show full response for debugging
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Function to get and process the data from a dataset CID
def get_data_for_year(cid):
    """Fetch the data for a given year and filter for Toyota cars based on 'Mfr Name'."""
    data = get_data_from_ipfs(cid)

    if data:
        try:
            # Read the dataset into pandas DataFrame
            df = pd.read_excel(data)

            # Clean up column names and data, only strip spaces and handle NaN where necessary
            df.columns = df.columns.str.strip()  # Strip spaces from column names
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)  # Strip spaces from object type columns
            
            # Ensure 'Mfr Name' is string type (only if it's not already)
            df['Mfr Name'] = df['Mfr Name'].astype(str)

            # Check if required columns exist
            if 'Mfr Name' not in df.columns or 'Comb FE (Guide) - Conventional Fuel' not in df.columns:
                print("Error: Required columns missing from the dataset.")
                return None

            # Drop rows where 'Mfr Name' or 'Comb FE (Guide) - Conventional Fuel' are NaN
            df = df.dropna(subset=['Mfr Name', 'Comb FE (Guide) - Conventional Fuel'])

            # Handle non-numeric values carefully
            # Convert 'Comb FE (Guide) - Conventional Fuel' to numeric, leave invalid strings as they are
            df['Comb FE (Guide) - Conventional Fuel'] = pd.to_numeric(df['Comb FE (Guide) - Conventional Fuel'], errors='coerce')

            # Filter dataset for Toyota cars using 'Mfr Name' column (case insensitive match)
            df_toyota = df[df['Mfr Name'].str.contains('TOYOTA', case=False, na=False)]

            if df_toyota.empty:
                print(f"No Toyota cars found in the data for CID {cid}.")
                return None

           
            return df_toyota

        except Exception as e:
            print(f"Error processing data: {e}")
            return None
    return None

# Main function to interact with the user
def main():
    # Get the year input from the user
    try:
        year = int(input("Enter the year for which you want to process data (2021 to 2025): "))
        if year not in [2021, 2022, 2023, 2024, 2025]:
            print("Invalid year. Please enter a valid year between 2021 and 2025.")
            return
    except ValueError:
        print("Invalid input. Please enter a numeric year between 2021 and 2025.")
        return

    # Match the CID based on the year
    cids = {
        "2025": os.getenv("FE_2025"),
        "2024": os.getenv("FE_2024"),
        "2023": os.getenv("FE_2023"),
        "2022": os.getenv("FE_2022"),
        "2021": os.getenv("FE_2021")
    }

    # Check if the CID for the given year exists
    cid = cids.get(str(year))
    if not cid:
        print(f"Error: No CID found for year {year}. Please check the environment variables.")
        return

    # Fetch and process data for the given CID
    df = get_data_for_year(cid)

    if df is not None:
        # Call the process function to find the most fuel-efficient Toyota car
        car, mpg = process_fuel_efficient_car(df, year)
        print(f"Car: {car}")
        print(f"MPG: {mpg}")
        

# Run the main function
if __name__ == "__main__":
    main()
