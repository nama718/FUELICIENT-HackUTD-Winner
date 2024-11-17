# visualizer.py

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def visualize_selected_columns(df: pd.DataFrame, selected_columns: list) -> plt.Figure:
    """
    Visualizes the selected columns from the Toyota dataset.

    Args:
        df (pd.DataFrame): The processed Toyota data.
        selected_columns (list): The list of columns to visualize.

    Returns:
        plt.Figure: A Matplotlib figure containing the plot.
    """
    if len(selected_columns) < 2:
        raise ValueError("Please select at least two columns for comparison.")
    
    # If only two columns are selected, create a scatter plot
    if len(selected_columns) == 2:
        col1, col2 = selected_columns
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(x=df[col1], y=df[col2], ax=ax)
        ax.set_title(f"{col1} vs {col2}")
        ax.set_xlabel(col1)
        ax.set_ylabel(col2)
        return fig

    # If more than two columns are selected, create a bar chart
    else:
        df_selected = df[selected_columns].mean().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10, 6))
        df_selected.plot(kind='bar', ax=ax, color='orange')
        ax.set_title(f"Comparison of {', '.join(selected_columns)}")
        ax.set_ylabel("Average Value")
        ax.set_xlabel("Columns")
        return fig
