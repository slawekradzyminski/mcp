"""Test configuration for unit tests."""

import sys
from unittest.mock import MagicMock

# Mock scikit-learn
mock_sklearn = MagicMock()
mock_sklearn.feature_extraction = MagicMock()
mock_sklearn.feature_extraction.text = MagicMock()
mock_sklearn.feature_extraction.text.TfidfVectorizer = MagicMock()
sys.modules["sklearn"] = mock_sklearn
sys.modules["sklearn.feature_extraction"] = mock_sklearn.feature_extraction
sys.modules["sklearn.feature_extraction.text"] = mock_sklearn.feature_extraction.text

# Mock the faiss module
mock_faiss = MagicMock()
sys.modules["faiss"] = mock_faiss
