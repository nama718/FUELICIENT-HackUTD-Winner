import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Function to visualize the selected columns
def visualize_selected_columns(df, selected_columns):
    # Display selected columns in the app
    st.subheader(f"Visualizing Selected Columns: {', '.join(selected_columns)}")

    # Ensure the columns are available in the dataframe
    if all(col in df.columns for col in selected_columns):
        # Separate numeric and non-numeric columns
        numeric_columns = [col for col in selected_columns if pd.api.types.is_numeric_dtype(df[col])]
        non_numeric_columns = [col for col in selected_columns if not pd.api.types.is_numeric_dtype(df[col])]

        # If there are numeric columns, generate plots
        if numeric_columns:
            # If only two numeric columns are selected, generate a scatter plot
            if len(numeric_columns) == 2:
                col1, col2 = numeric_columns
                st.write(f"### Scatter Plot of {col1} vs {col2}")
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.scatterplot(x=df[col1], y=df[col2], ax=ax)
                ax.set_title(f"{col1} vs {col2}")
                ax.set_xlabel(col1)
                ax.set_ylabel(col2)
                st.pyplot(fig)

            # If more than two columns are selected, create a bar chart for comparison
            else:
                st.write(f"### Bar Chart of {', '.join(numeric_columns)}")
                df_selected = df[numeric_columns].mean().sort_values(ascending=False)
                fig, ax = plt.subplots(figsize=(10, 6))
                df_selected.plot(kind='bar', ax=ax, color='orange')
                ax.set_title(f"Comparison of {', '.join(numeric_columns)}")
                ax.set_ylabel("Average Value")
                ax.set_xlabel("Columns")
                st.pyplot(fig)

        # Handle non-numeric columns (just display them)
        if non_numeric_columns:
            st.write(f"### Non-Numeric Columns Selected: {', '.join(non_numeric_columns)}")
            st.dataframe(df[non_numeric_columns])
            
        # Show an error if there's no valid numeric columns
        if not numeric_columns and not non_numeric_columns:
            st.error("No valid columns selected for visualization.")
    else:
        st.error(f"One or more of the selected columns are missing from the data: {', '.join(selected_columns)}")