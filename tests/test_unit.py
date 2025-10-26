"""
Unit tests for core portfolio website functionality.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, Mock
from app import (
    generate_text_cache_key, 
    generate_prediction_cache_key,
    save_contact_submission,
    init_contact_file,
    train_pass_predictor_model
)

class TestUtilityFunctions:
    """Test utility and helper functions."""

    @pytest.mark.unit
    def test_generate_text_cache_key(self):
        """Test text cache key generation."""
        text1 = "Hello world"
        text2 = "Hello world"
        text3 = "Different text"
        
        key1 = generate_text_cache_key(text1)
        key2 = generate_text_cache_key(text2)
        key3 = generate_text_cache_key(text3)
        
        # Same text should generate same key
        assert key1 == key2
        # Different text should generate different key
        assert key1 != key3
        # Key should have proper prefix
        assert key1.startswith("mood_analysis:")

    @pytest.mark.unit
    def test_generate_prediction_cache_key(self):
        """Test prediction cache key generation."""
        data1 = {
            'study_hours': 8,
            'sleep_hours': 7,
            'attendance': 85,
            'class_avg_score': 78,
            'student_test_score': 82,
            'student_assignment_score': 80,
            'num_failed_before': 0,
            'participation_score': 8
        }
        
        data2 = data1.copy()
        data3 = data1.copy()
        data3['study_hours'] = 9  # Different value
        
        key1 = generate_prediction_cache_key(data1)
        key2 = generate_prediction_cache_key(data2)
        key3 = generate_prediction_cache_key(data3)
        
        # Same data should generate same key
        assert key1 == key2
        # Different data should generate different key
        assert key1 != key3
        # Key should have proper prefix
        assert key1.startswith("pass_prediction:")

    @pytest.mark.unit
    def test_init_contact_file(self, tmp_path):
        """Test contact file initialization."""
        # Test with non-existent file
        contact_file = tmp_path / "test_contacts.json"
        
        with patch('app.CONTACT_FILE', str(contact_file)):
            init_contact_file()
            
            # File should be created with empty array
            assert contact_file.exists()
            
            with open(contact_file, 'r') as f:
                data = json.load(f)
                assert data == []

    @pytest.mark.unit
    def test_save_contact_submission(self, tmp_path):
        """Test saving contact submissions."""
        contact_file = tmp_path / "test_contacts.json"
        
        # Initialize with empty file
        with open(contact_file, 'w') as f:
            json.dump([], f)
        
        test_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message'
        }
        
        with patch('app.CONTACT_FILE', str(contact_file)):
            result = save_contact_submission(test_data)
            
            assert result is True
            
            # Check file contents
            with open(contact_file, 'r') as f:
                submissions = json.load(f)
                
            assert len(submissions) == 1
            assert submissions[0]['name'] == 'Test User'
            assert submissions[0]['email'] == 'test@example.com'
            assert submissions[0]['id'] == 1
            assert 'timestamp' in submissions[0]

    @pytest.mark.unit
    @pytest.mark.slow
    def test_train_pass_predictor_model(self):
        """Test ML model training function."""
        model, scaler, accuracy = train_pass_predictor_model()
        
        # Check that we get valid objects
        assert model is not None
        assert scaler is not None
        assert isinstance(accuracy, float)
        assert 0.0 <= accuracy <= 1.0
        
        # Test model has required methods
        assert hasattr(model, 'predict')
        assert hasattr(model, 'predict_proba')
        assert hasattr(scaler, 'transform')


class TestCachingFunctions:
    """Test caching functionality."""

    @pytest.mark.unit
    def test_cache_key_consistency(self):
        """Test that cache keys are consistent for same input."""
        # Test text cache keys
        text = "This is a test sentence for caching."
        key1 = generate_text_cache_key(text)
        key2 = generate_text_cache_key(text)
        assert key1 == key2
        
        # Test prediction cache keys
        data = {
            'study_hours': 5,
            'sleep_hours': 8,
            'attendance': 90,
            'class_avg_score': 85,
            'student_test_score': 88,
            'student_assignment_score': 87,
            'num_failed_before': 1,
            'participation_score': 7
        }
        
        pred_key1 = generate_prediction_cache_key(data)
        pred_key2 = generate_prediction_cache_key(data)
        assert pred_key1 == pred_key2

    @pytest.mark.unit
    def test_cache_key_uniqueness(self):
        """Test that different inputs generate different cache keys."""
        # Different texts
        key1 = generate_text_cache_key("Hello world")
        key2 = generate_text_cache_key("Goodbye world")
        assert key1 != key2
        
        # Different prediction data
        data1 = {'study_hours': 5, 'sleep_hours': 8, 'attendance': 90, 'class_avg_score': 85,
                'student_test_score': 88, 'student_assignment_score': 87, 'num_failed_before': 1,
                'participation_score': 7}
        
        data2 = data1.copy()
        data2['study_hours'] = 6
        
        pred_key1 = generate_prediction_cache_key(data1)
        pred_key2 = generate_prediction_cache_key(data2)
        assert pred_key1 != pred_key2


class TestDataValidation:
    """Test data validation and edge cases."""

    @pytest.mark.unit
    def test_empty_contact_data(self, tmp_path):
        """Test handling of incomplete contact data."""
        contact_file = tmp_path / "test_contacts.json"
        
        with open(contact_file, 'w') as f:
            json.dump([], f)
        
        # Test with missing fields - should return False
        incomplete_data = {'name': 'Test User'}  # Missing other fields
        
        with patch('app.CONTACT_FILE', str(contact_file)):
            # This should return False since required fields are missing
            result = save_contact_submission(incomplete_data)
            assert result is False

    @pytest.mark.unit 
    def test_unicode_text_cache_key(self):
        """Test cache key generation with unicode text."""
        unicode_text = "Hello 世界! 🌍 émojis and ñoñ-ASCII characters"
        key = generate_text_cache_key(unicode_text)
        
        assert isinstance(key, str)
        assert key.startswith("mood_analysis:")
        
        # Should be consistent
        key2 = generate_text_cache_key(unicode_text)
        assert key == key2

    @pytest.mark.unit
    def test_extreme_prediction_values(self):
        """Test prediction cache key with extreme values."""
        extreme_data = {
            'study_hours': 0,  # Minimum
            'sleep_hours': 24,  # Maximum 
            'attendance': 100,  # Maximum
            'class_avg_score': 0,  # Minimum
            'student_test_score': 100,  # Maximum
            'student_assignment_score': 0,  # Minimum
            'num_failed_before': 10,  # High value
            'participation_score': 0  # Minimum
        }
        
        key = generate_prediction_cache_key(extreme_data)
        assert isinstance(key, str)
        assert key.startswith("pass_prediction:")


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.unit
    def test_save_contact_submission_file_error(self, tmp_path):
        """Test contact submission when file operations fail."""
        # Point to a directory that doesn't exist
        nonexistent_file = tmp_path / "nonexistent" / "contacts.json"
        
        test_data = {
            'name': 'Test User',
            'email': 'test@example.com', 
            'subject': 'Test Subject',
            'message': 'Test message'
        }
        
        with patch('app.CONTACT_FILE', str(nonexistent_file)):
            result = save_contact_submission(test_data)
            # Should return False when file operations fail
            assert result is False

    @pytest.mark.unit
    def test_corrupted_contact_file(self, tmp_path):
        """Test handling of corrupted contact file."""
        contact_file = tmp_path / "corrupted_contacts.json"
        
        # Create corrupted JSON file
        with open(contact_file, 'w') as f:
            f.write('{"invalid": json}')  # Invalid JSON
        
        test_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject', 
            'message': 'Test message'
        }
        
        with patch('app.CONTACT_FILE', str(contact_file)):
            result = save_contact_submission(test_data)
            # Should handle JSON decode error gracefully
            assert result is False
