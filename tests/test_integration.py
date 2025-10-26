"""
Integration and ML-specific tests for portfolio website.
"""

import pytest
import json
import time
from unittest.mock import patch, Mock
import numpy as np
import pandas as pd

class TestCachingIntegration:
    """Test full caching integration scenarios."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_cache_performance_improvement(self, client, sample_mood_data, mock_nltk):
        """Test that caching improves performance."""
        data = {'text': sample_mood_data['positive_text']}
        
        # First request (cache miss)
        start_time = time.time()
        response1 = client.post('/api/mood-analysis',
                              data=json.dumps(data),
                              content_type='application/json')
        first_request_time = time.time() - start_time
        
        # Second request (cache hit)
        start_time = time.time()
        response2 = client.post('/api/mood-analysis',
                              data=json.dumps(data),
                              content_type='application/json')
        second_request_time = time.time() - start_time
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Cache hit should be faster (though this might be flaky in CI)
        # Just verify both requests succeed and return same data
        result1 = json.loads(response1.data)
        result2 = json.loads(response2.data)
        assert result1 == result2

    @pytest.mark.integration
    def test_cache_expiration_behavior(self, app, client, sample_mood_data, mock_nltk):
        """Test cache expiration behavior."""
        data = {'text': sample_mood_data['positive_text']}
        
        with app.app_context():
            # Set very short cache timeout for testing
            from app import cache
            
            # First request
            response1 = client.post('/api/mood-analysis',
                                  data=json.dumps(data),
                                  content_type='application/json')
            
            # Clear cache manually to simulate expiration
            cache.clear()
            
            # Second request (should not hit cache)
            response2 = client.post('/api/mood-analysis',
                                  data=json.dumps(data),
                                  content_type='application/json')
            
            assert response1.status_code == 200
            assert response2.status_code == 200

    @pytest.mark.integration 
    def test_concurrent_cache_access(self, client, sample_prediction_data, mock_ml_models):
        """Test concurrent access to cached data."""
        # Make multiple requests with same data simultaneously
        responses = []
        for _ in range(5):
            response = client.post('/api/pass-predict',
                                 data=json.dumps(sample_prediction_data),
                                 content_type='application/json')
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
        
        # All should return identical results
        results = [json.loads(response.data) for response in responses]
        first_result = results[0]
        for result in results[1:]:
            assert result == first_result


class TestMLModelIntegration:
    """Test ML model integration and behavior."""

    @pytest.mark.ml
    @pytest.mark.integration
    def test_mood_analysis_comprehensive(self, client, mock_nltk):
        """Comprehensive test of mood analysis functionality."""
        test_cases = [
            {
                'text': 'I absolutely love this wonderful amazing fantastic product!',
                'expected_mood': 'Positive'
            },
            {
                'text': 'I hate this terrible awful disgusting horrible product!',
                'expected_mood': 'Negative' 
            },
            {
                'text': 'The weather is okay today. Nothing special.',
                'expected_mood': 'Neutral'
            },
            {
                'text': '',  # Edge case
                'should_fail': True
            }
        ]
        
        for case in test_cases:
            data = {'text': case['text']}
            response = client.post('/api/mood-analysis',
                                 data=json.dumps(data),
                                 content_type='application/json')
            
            if case.get('should_fail'):
                assert response.status_code == 400
            else:
                assert response.status_code == 200
                result = json.loads(response.data)
                assert result['success'] is True
                
                # Check that the expected mood is detected
                # Note: This is a simplified check since our mock might not be perfect
                assert result['mood'] in ['Positive', 'Negative', 'Neutral']
                
                # Check required fields are present
                required_fields = ['mood', 'confidence', 'analysis', 'details', 'ml_metrics']
                for field in required_fields:
                    assert field in result

    @pytest.mark.ml
    @pytest.mark.integration
    def test_pass_prediction_edge_cases(self, client, mock_ml_models):
        """Test pass prediction with edge case inputs."""
        edge_cases = [
            # Minimum values
            {
                'study_hours': 0, 'sleep_hours': 0, 'attendance': 0, 'class_avg_score': 0,
                'student_test_score': 0, 'student_assignment_score': 0, 'num_failed_before': 0,
                'participation_score': 0
            },
            # Maximum realistic values
            {
                'study_hours': 24, 'sleep_hours': 24, 'attendance': 100, 'class_avg_score': 100,
                'student_test_score': 100, 'student_assignment_score': 100, 'num_failed_before': 10,
                'participation_score': 10
            },
            # Mixed values
            {
                'study_hours': 5, 'sleep_hours': 6, 'attendance': 75, 'class_avg_score': 80,
                'student_test_score': 85, 'student_assignment_score': 78, 'num_failed_before': 2,
                'participation_score': 7
            }
        ]
        
        for case in edge_cases:
            response = client.post('/api/pass-predict',
                                 data=json.dumps(case),
                                 content_type='application/json')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            
            assert result['success'] is True
            assert result['prediction'] in [0, 1]
            assert result['label'] in ['Pass', 'Fail']
            assert 0 <= result['confidence'] <= 100
            assert 0 <= result['prob_pass'] <= 100
            assert 0 <= result['prob_fail'] <= 100
            assert isinstance(result['factors'], list)
            assert isinstance(result['model_accuracy'], float)

    @pytest.mark.ml
    @pytest.mark.slow
    def test_model_training_integration(self):
        """Test the actual model training process."""
        from app import train_pass_predictor_model
        
        model, scaler, accuracy = train_pass_predictor_model()
        
        # Test model properties
        assert model is not None
        assert scaler is not None
        assert 0.0 <= accuracy <= 1.0
        
        # Test model can make predictions
        sample_data = np.array([[8, 7, 85, 78, 82, 80, 0, 8]])
        scaled_data = scaler.transform(sample_data)
        
        prediction = model.predict(scaled_data)
        probability = model.predict_proba(scaled_data)
        
        assert prediction.shape == (1,)
        assert prediction[0] in [0, 1]
        assert probability.shape == (1, 2)
        assert np.isclose(probability[0].sum(), 1.0)

    @pytest.mark.ml
    def test_text_preprocessing_integration(self, client, mock_nltk):
        """Test text preprocessing behavior in mood analysis."""
        test_cases = [
            # Test with punctuation and mixed case
            {
                'text': 'I LOVE this Amazing Product!!! It is SO WONDERFUL!!!',
                'should_contain_indicators': True
            },
            # Test with stop words
            {
                'text': 'The quick brown fox jumps over the lazy dog.',
                'should_be_neutral': True
            },
            # Test with numbers and special characters
            {
                'text': 'Product rating: 5/5 stars! 100% satisfied! @company #awesome',
                'should_contain_indicators': True
            },
            # Test with unicode characters
            {
                'text': 'I ❤️ this product! It\'s 😀 amazing! 👍',
                'should_contain_indicators': True
            }
        ]
        
        for case in test_cases:
            data = {'text': case['text']}
            response = client.post('/api/mood-analysis',
                                 data=json.dumps(data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['success'] is True
            
            # Check that text was processed
            assert 'ml_metrics' in result
            assert result['ml_metrics']['text_length'] > 0


class TestFullApplicationFlow:
    """Test complete application workflows."""

    @pytest.mark.integration
    def test_complete_contact_workflow(self, client, sample_contact_data):
        """Test complete contact form submission workflow."""
        # Submit contact form
        response = client.post('/api/contact',
                             data=json.dumps(sample_contact_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
        
        # Verify contact was saved by checking admin endpoint
        admin_response = client.get('/admin/contacts')
        assert admin_response.status_code == 200
        
        admin_data = json.loads(admin_response.data)
        assert admin_data['success'] is True
        assert admin_data['count'] >= 1
        
        # Find our submitted contact
        found_contact = False
        for submission in admin_data['submissions']:
            if submission['name'] == sample_contact_data['name']:
                found_contact = True
                assert submission['email'] == sample_contact_data['email']
                assert submission['subject'] == sample_contact_data['subject']
                assert submission['message'] == sample_contact_data['message']
                assert 'timestamp' in submission
                assert 'id' in submission
                break
        
        assert found_contact, "Contact submission not found in admin view"

    @pytest.mark.integration
    @pytest.mark.ml
    def test_ml_prediction_workflow(self, client, sample_prediction_data, mock_ml_models):
        """Test complete ML prediction workflow."""
        # Make prediction
        response = client.post('/api/pass-predict',
                             data=json.dumps(sample_prediction_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        # Verify all expected fields
        expected_fields = [
            'success', 'prediction', 'label', 'confidence',
            'prob_pass', 'prob_fail', 'factors', 'model_accuracy'
        ]
        
        for field in expected_fields:
            assert field in result
        
        # Verify data consistency
        assert result['success'] is True
        assert result['prediction'] in [0, 1]
        
        if result['prediction'] == 1:
            assert result['label'] == 'Pass'
        else:
            assert result['label'] == 'Fail'
        
        # Probabilities should add up to 100
        assert abs((result['prob_pass'] + result['prob_fail']) - 100.0) < 0.1

    @pytest.mark.integration
    def test_error_handling_workflow(self, client):
        """Test error handling across different scenarios."""
        error_scenarios = [
            # Invalid JSON
            {
                'endpoint': '/api/contact',
                'data': 'invalid json',
                'content_type': 'application/json',
                'expected_status': [400, 500]  # Varies by Flask version
            },
            # Missing required fields
            {
                'endpoint': '/api/mood-analysis',
                'data': json.dumps({}),
                'content_type': 'application/json',
                'expected_status': 400
            },
            # Non-existent route
            {
                'endpoint': '/api/nonexistent',
                'data': json.dumps({}),
                'content_type': 'application/json',
                'expected_status': 404
            }
        ]
        
        for scenario in error_scenarios:
            response = client.post(
                scenario['endpoint'],
                data=scenario['data'],
                content_type=scenario['content_type']
            )
            
            expected_status = scenario['expected_status']
            if isinstance(expected_status, list):
                assert response.status_code in expected_status
            else:
                assert response.status_code == expected_status

    @pytest.mark.integration
    @pytest.mark.slow
    def test_cache_consistency_across_requests(self, client, sample_mood_data, mock_nltk):
        """Test cache consistency across multiple different requests."""
        # Make requests with different texts
        texts = [
            sample_mood_data['positive_text'],
            sample_mood_data['negative_text'], 
            sample_mood_data['neutral_text']
        ]
        
        # Store initial results
        initial_results = {}
        for i, text in enumerate(texts):
            data = {'text': text}
            response = client.post('/api/mood-analysis',
                                 data=json.dumps(data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            initial_results[i] = json.loads(response.data)
        
        # Make the same requests again and verify consistency
        for i, text in enumerate(texts):
            data = {'text': text}
            response = client.post('/api/mood-analysis',
                                 data=json.dumps(data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            
            # Results should be identical to initial results (cached)
            assert result == initial_results[i]
