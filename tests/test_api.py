"""
API endpoint tests for portfolio website.
"""

import pytest
import json
from unittest.mock import patch, Mock

class TestRouteAccessibility:
    """Test basic route accessibility."""

    @pytest.mark.api
    def test_home_page(self, client):
        """Test home page accessibility."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Rishab' in response.data

    @pytest.mark.api
    def test_demo_routes(self, client):
        """Test all demo routes are accessible."""
        demo_routes = [
            '/demo/mood-detector',
            '/demo/pass-predictor'
        ]
        
        for route in demo_routes:
            response = client.get(route)
            assert response.status_code == 200, f"Route {route} failed"

    @pytest.mark.api
    def test_404_error_handler(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent-route')
        assert response.status_code == 404


class TestContactAPI:
    """Test contact form API endpoints."""

    @pytest.mark.api
    def test_api_contact_success(self, client, sample_contact_data):
        """Test successful contact form submission."""
        response = client.post('/api/contact', 
                             data=json.dumps(sample_contact_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Message saved!' in data['message']

    @pytest.mark.api
    def test_api_contact_missing_fields(self, client):
        """Test contact form with missing fields."""
        incomplete_data = {
            'name': 'Test User',
            'email': 'test@example.com'
            # Missing subject and message
        }
        
        response = client.post('/api/contact',
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Please fill all fields!' in data['message']

    @pytest.mark.api
    def test_api_contact_empty_json(self, client):
        """Test contact form with empty JSON."""
        response = client.post('/api/contact',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    @pytest.mark.api
    def test_admin_contacts_view(self, client, sample_contact_data):
        """Test admin contacts viewing endpoint."""
        # First submit a contact
        client.post('/api/contact',
                   data=json.dumps(sample_contact_data),
                   content_type='application/json')
        
        # Then view contacts
        response = client.get('/admin/contacts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['count'] >= 1
        assert len(data['submissions']) >= 1


class TestMoodAnalysisAPI:
    """Test mood analysis API endpoints."""

    @pytest.mark.api
    @pytest.mark.ml
    def test_mood_analysis_positive(self, client, sample_mood_data, mock_nltk):
        """Test mood analysis with positive text."""
        data = {'text': sample_mood_data['positive_text']}
        
        response = client.post('/api/mood-analysis',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['success'] is True
        assert result['mood'] in ['Positive', 'Negative', 'Neutral']
        assert 'confidence' in result
        assert 'analysis' in result
        assert 'details' in result
        assert 'ml_metrics' in result

    @pytest.mark.api
    @pytest.mark.ml
    def test_mood_analysis_negative(self, client, sample_mood_data, mock_nltk):
        """Test mood analysis with negative text."""
        data = {'text': sample_mood_data['negative_text']}
        
        response = client.post('/api/mood-analysis',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['success'] is True
        assert result['mood'] in ['Positive', 'Negative', 'Neutral']

    @pytest.mark.api
    @pytest.mark.ml
    def test_mood_analysis_neutral(self, client, sample_mood_data, mock_nltk):
        """Test mood analysis with neutral text."""
        data = {'text': sample_mood_data['neutral_text']}
        
        response = client.post('/api/mood-analysis',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['success'] is True
        assert result['mood'] in ['Positive', 'Negative', 'Neutral']

    @pytest.mark.api
    def test_mood_analysis_empty_text(self, client):
        """Test mood analysis with empty text."""
        data = {'text': ''}
        
        response = client.post('/api/mood-analysis',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert result['success'] is False
        assert 'Please provide text for analysis' in result['message']

    @pytest.mark.api
    def test_mood_analysis_no_text_field(self, client):
        """Test mood analysis without text field."""
        data = {'not_text': 'some content'}
        
        response = client.post('/api/mood-analysis',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert result['success'] is False

    @pytest.mark.api
    @pytest.mark.ml
    def test_mood_analysis_caching(self, client, sample_mood_data, mock_nltk):
        """Test mood analysis caching functionality."""
        data = {'text': sample_mood_data['positive_text']}
        
        # First request
        response1 = client.post('/api/mood-analysis',
                              data=json.dumps(data),
                              content_type='application/json')
        
        # Second request (should hit cache)
        response2 = client.post('/api/mood-analysis',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        result1 = json.loads(response1.data)
        result2 = json.loads(response2.data)
        
        # Results should be identical (from cache)
        assert result1 == result2


class TestPassPredictorAPI:
    """Test pass predictor API endpoints."""

    @pytest.mark.api
    @pytest.mark.ml
    def test_pass_predict_success(self, client, sample_prediction_data, mock_ml_models):
        """Test successful pass prediction."""
        response = client.post('/api/pass-predict',
                             data=json.dumps(sample_prediction_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['success'] is True
        assert 'prediction' in result
        assert 'label' in result
        assert 'confidence' in result
        assert 'prob_pass' in result
        assert 'prob_fail' in result
        assert 'factors' in result
        assert 'model_accuracy' in result
        
        # Check prediction is 0 or 1
        assert result['prediction'] in [0, 1]
        # Check label matches prediction
        expected_label = 'Pass' if result['prediction'] == 1 else 'Fail'
        assert result['label'] == expected_label

    @pytest.mark.api
    def test_pass_predict_missing_fields(self, client):
        """Test pass prediction with missing fields."""
        incomplete_data = {
            'study_hours': 8,
            'sleep_hours': 7
            # Missing other required fields
        }
        
        response = client.post('/api/pass-predict',
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert result['success'] is False
        assert 'Missing fields' in result['message']

    @pytest.mark.api
    @pytest.mark.ml
    def test_pass_predict_caching(self, client, sample_prediction_data, mock_ml_models):
        """Test pass prediction caching functionality."""
        # First request
        response1 = client.post('/api/pass-predict',
                              data=json.dumps(sample_prediction_data),
                              content_type='application/json')
        
        # Second request with same data (should hit cache)
        response2 = client.post('/api/pass-predict',
                              data=json.dumps(sample_prediction_data),
                              content_type='application/json')
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        result1 = json.loads(response1.data)
        result2 = json.loads(response2.data)
        
        # Results should be identical (from cache)
        assert result1 == result2

    @pytest.mark.api
    @pytest.mark.ml
    def test_pass_predict_different_inputs(self, client, mock_ml_models):
        """Test pass prediction with different inputs."""
        data1 = {
            'study_hours': 8, 'sleep_hours': 7, 'attendance': 85, 'class_avg_score': 78,
            'student_test_score': 82, 'student_assignment_score': 80, 'num_failed_before': 0,
            'participation_score': 8
        }
        
        data2 = data1.copy()
        data2['study_hours'] = 4  # Different value
        
        response1 = client.post('/api/pass-predict',
                              data=json.dumps(data1),
                              content_type='application/json')
        
        response2 = client.post('/api/pass-predict',
                              data=json.dumps(data2),
                              content_type='application/json')
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Both should succeed
        result1 = json.loads(response1.data)
        result2 = json.loads(response2.data)
        
        assert result1['success'] is True
        assert result2['success'] is True


class TestCodeExecutionAPI:
    """Test code execution API endpoints."""

    @pytest.mark.api
    def test_execute_code_no_code(self, client):
        """Test code execution without code."""
        data = {'language': 'python'}
        
        response = client.post('/api/execute-code',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert result['success'] is False
        assert 'No code provided' in result['error']

    @pytest.mark.api
    def test_execute_code_invalid_json(self, client):
        """Test code execution with invalid JSON."""
        response = client.post('/api/execute-code',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code in [400, 500]  # Depends on Flask version


class TestCachingIntegration:
    """Test caching integration across API endpoints."""

    @pytest.mark.api
    @pytest.mark.integration
    def test_cache_isolation(self, client, sample_mood_data, sample_prediction_data, mock_nltk, mock_ml_models):
        """Test that different API caches don't interfere with each other."""
        # Make mood analysis request
        mood_data = {'text': sample_mood_data['positive_text']}
        mood_response = client.post('/api/mood-analysis',
                                  data=json.dumps(mood_data),
                                  content_type='application/json')
        
        # Make prediction request
        pred_response = client.post('/api/pass-predict',
                                  data=json.dumps(sample_prediction_data),
                                  content_type='application/json')
        
        assert mood_response.status_code == 200
        assert pred_response.status_code == 200
        
        # Both should work independently
        mood_result = json.loads(mood_response.data)
        pred_result = json.loads(pred_response.data)
        
        assert mood_result['success'] is True
        assert pred_result['success'] is True

    @pytest.mark.api
    def test_cache_headers_not_exposed(self, client, sample_mood_data, mock_nltk):
        """Test that cache implementation details aren't exposed in responses."""
        data = {'text': sample_mood_data['positive_text']}
        
        response = client.post('/api/mood-analysis',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        
        # Response shouldn't contain cache-related headers or data
        assert 'cache-control' not in response.headers.get('Content-Type', '').lower()
        
        result = json.loads(response.data)
        # Result shouldn't contain cache metadata
        assert 'cache_key' not in result
        assert 'cached' not in result
