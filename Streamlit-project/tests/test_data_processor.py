# tests/test_data_processor.py

import pytest
import pandas as pd
from data_processor import get_data_for_year

def test_get_data_for_year_valid_data():
    mock_data = {
        'Mfr Name': ['TOYOTA', 'TOYOTA', 'FORD'],
        'Carline': ['Corolla', 'Camry', 'Fusion'],
        'Comb FE (Guide) - Conventional Fuel': [30, 28, 25],
        'Eng Displ': [1.8, 2.5, 2.0],
        'City CO2 Rounded Adjusted': [320, 330, 340],
        'Hwy CO2 Rounded Adjusted': [250, 260, 270]
    }
    df = pd.DataFrame(mock_data)
    result = get_data_for_year(df)
    assert not result.empty
    assert 'TOYOTA' in result['Mfr Name'].values

def test_get_data_for_year_no_toyota():
    mock_data = {
        'Mfr Name': ['FORD', 'HONDA'],
        'Carline': ['Fusion', 'Civic'],
        'Comb FE (Guide) - Conventional Fuel': [25, 30],
        'Eng Displ': [2.0, 1.8],
        'City CO2 Rounded Adjusted': [340, 320],
        'Hwy CO2 Rounded Adjusted': [270, 250]
    }
    df = pd.DataFrame(mock_data)
    result = get_data_for_year(df)
    assert result.empty
