# tests/test_data_fetcher.py

import pytest
from unittest.mock import patch
from data_fetcher import get_data_from_ipfs

def test_get_data_from_ipfs_success():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"dummy content"
        result = get_data_from_ipfs("dummy_cid")
        assert result is not None
        assert isinstance(result, BytesIO)

def test_get_data_from_ipfs_failure():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        result = get_data_from_ipfs("dummy_cid")
        assert result is None
