import unittest
from unittest.mock import Mock, patch
import requests
from firebase_client import sign_in, FirebaseError
from rag import OllamaClient, RagError


class ServiceTests(unittest.TestCase):
    def test_network_failure_becomes_safe_error(self):
        with patch('rag.requests.post', side_effect=requests.ConnectionError('sensitive raw URL')):
            with self.assertRaises(RagError) as error:
                OllamaClient('http://localhost:11434').embed(['test'])
            self.assertNotIn('sensitive', str(error.exception))

    def test_firebase_invalid_password(self):
        response = Mock(ok=False)
        response.json.return_value = {'error': {'message': 'INVALID_LOGIN_CREDENTIALS'}}
        with patch('firebase_client.FIREBASE_API_KEY', 'fake'), patch('firebase_client.FIREBASE_PROJECT_ID', 'fake'), patch('firebase_client.requests.post', return_value=response):
            with self.assertRaises(FirebaseError) as error:
                sign_in('a@example.test', 'wrong')
            self.assertIn('mật khẩu', str(error.exception))

    def test_invalid_json_is_service_error(self):
        response = Mock(ok=True, status_code=200)
        response.json.side_effect = ValueError()
        with patch('rag.requests.post', return_value=response):
            with self.assertRaises(RagError):
                OllamaClient('http://localhost:11434').embed(['test'])
