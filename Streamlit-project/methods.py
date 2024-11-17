import pandas as pd

def find_most_fuel_efficient_car(df):
    """Find the most fuel-efficient car based on combined fuel efficiency."""
    try:
        # Ensure that 'Comb FE (Guide) - Conventional Fuel' column exists
        if 'Comb FE (Guide) - Conventional Fuel' not in df.columns:
            print("Error: 'Comb FE (Guide) - Conventional Fuel' column is missing.")
            return None
        
        if 'Carline' not in df.columns:
            print("Error: 'Carline' column is missing.")
            return None
        
        # Drop rows with missing fuel efficiency or carline values
        df_clean = df.dropna(subset=['Comb FE (Guide) - Conventional Fuel', 'Carline'])
        
        # Check if the dataframe has any rows left after cleaning
        if df_clean.empty:
            print("Error: No valid data available after cleaning.")
            return None
        
        # Find the car with the highest combined fuel efficiency
        most_fuel_efficient_car = df_clean.loc[df_clean['Comb FE (Guide) - Conventional Fuel'].idxmax()]
        
        # Return the entire row, which includes car details and fuel efficiency
        return most_fuel_efficient_car
    
    except Exception as e:
        print(f"Error finding most fuel-efficient car: {e}")
        return None

def process_fuel_efficient_car(df, year):
    """Process and print the most fuel-efficient car's fuel efficiency for the given year."""
    most_fuel_efficient_car = find_most_fuel_efficient_car(df)

    if most_fuel_efficient_car is not None:
        # Print the most fuel-efficient car's details (only required information)
        carline = most_fuel_efficient_car['Carline']
        fuel_efficiency = most_fuel_efficient_car['Comb FE (Guide) - Conventional Fuel']
        
        # Only print the necessary information
        print(f"The most fuel-efficient car for year {year} is {carline} "
              f"with a combined fuel efficiency of {fuel_efficiency} MPG.")
        return (carline,fuel_efficiency)
    else:
        print(f"Could not determine the most fuel-efficient Toyota car for {year}.")
