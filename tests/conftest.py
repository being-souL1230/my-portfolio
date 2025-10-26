"""
Test configuration and fixtures for portfolio website tests.
"""

import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch
import sys

# Add the parent directory to sys.path so we can import our app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app, cache, init_contact_file

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file for testing database
    db_fd, flask_app.config['DATABASE'] = tempfile.mkstemp()
    flask_app.config['TESTING'] = True
    flask_app.config['CACHE_TYPE'] = 'SimpleCache'
    flask_app.config['WTF_CSRF_ENABLED'] = False
    
    with flask_app.app_context():
        init_contact_file()
        yield flask_app
    
    os.close(db_fd)
    os.unlink(flask_app.config['DATABASE'])

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def sample_contact_data():
    """Sample contact form data for testing."""
    return {
        'name': 'Test User',
        'email': 'test@example.com',
        'subject': 'Test Subject',
        'message': 'This is a test message.'
    }

@pytest.fixture
def sample_mood_data():
    """Sample mood analysis data for testing."""
    return {
        'positive_text': 'I love this amazing product! It is fantastic and wonderful.',
        'negative_text': 'I hate this terrible product! It is awful and disgusting.',
        'neutral_text': 'The weather is okay today. It is normal and regular.'
    }

@pytest.fixture
def sample_prediction_data():
    """Sample prediction data for testing."""
    return {
        'study_hours': 8,
        'sleep_hours': 7,
        'attendance': 85,
        'class_avg_score': 78,
        'student_test_score': 82,
        'student_assignment_score': 80,
        'num_failed_before': 0,
        'participation_score': 8
    }

@pytest.fixture
def mock_ml_models():
    """Mock ML models for testing without loading actual models."""
    with patch('app.PASS_MODEL') as mock_model, \
         patch('app.PASS_SCALER') as mock_scaler, \
         patch('app.PASS_MODEL_ACC', 0.85):
        
        # Configure mock model behavior
        mock_model.predict.return_value = [1]  # Pass prediction
        mock_model.predict_proba.return_value = [[0.2, 0.8]]  # 80% confidence
        
        # Configure mock scaler behavior
        mock_scaler.transform.return_value = [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]]
        
        yield {
            'model': mock_model,
            'scaler': mock_scaler
        }

@pytest.fixture
def temp_contact_file():
    """Create a temporary contact file for testing."""
    # Create temporary file
    fd, path = tempfile.mkstemp(suffix='.json')
    
    # Write initial empty array
    with open(path, 'w') as f:
        json.dump([], f)
    
    yield path
    
    # Clean up
    os.close(fd)
    os.unlink(path)

@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    with flask_app.app_context():
        cache.clear()
        yield
        cache.clear()

@pytest.fixture
def mock_nltk():
    """Mock NLTK components to avoid downloading data during tests."""
    with patch('builtins.__import__') as mock_import:
        def side_effect(name, *args):
            if name == 'nltk':
                # Create mock NLTK module
                mock_nltk = Mock()
                mock_nltk.data.find.return_value = True
                mock_nltk.download.return_value = True
                
                # Mock stopwords
                mock_nltk.corpus.stopwords.words.return_value = [
                    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'
                ]
                
                return mock_nltk
            elif name == 'nltk.corpus':
                mock_corpus = Mock()
                mock_corpus.stopwords.words.return_value = [
                    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'
                ]
                return mock_corpus
            elif name == 'nltk.stem':
                mock_stem = Mock()
                mock_lemmatizer = Mock()
                mock_lemmatizer.lemmatize.side_effect = lambda word: word.lower()
                mock_stem.WordNetLemmatizer.return_value = mock_lemmatizer
                return mock_stem
            else:
                # Return the original import for other modules
                return original_import(name, *args)
        
        original_import = __builtins__['__import__']
        mock_import.side_effect = side_effect
        
        yield mock_import
