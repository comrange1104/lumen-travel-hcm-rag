import unittest
from unittest.mock import Mock, patch
import requests
from firebase_client import sign_in, FirebaseError
from rag import OllamaClient, RagError


class ServiceTests(unittest.TestCase):
    def test_health_check_rejects_html_in_place_of_ollama(self):
        from scripts.start_recording import healthy
        response = Mock(ok=True)
        response.json.side_effect = ValueError()
        with patch('scripts.start_recording.requests.get', return_value=response):
            self.assertFalse(healthy('https://old.free.pinggy.net/api/tags'))

    def test_stale_client_reuses_a_healthy_already_renewed_tunnel(self):
        from ollama_runtime import recover_tunnel
        with patch('ollama_runtime.dotenv_values', return_value={'OLLAMA_BASE_URL': 'https://new.free.pinggy.net'}), patch('scripts.start_recording.healthy', return_value=True), patch('scripts.start_recording.ensure_services') as start:
            self.assertEqual(recover_tunnel('https://old.free.pinggy.net'), 'https://new.free.pinggy.net')
            start.assert_not_called()
    def test_expired_pinggy_recovers_once_and_retries_the_real_request(self):
        response = Mock(ok=True, status_code=200)
        response.json.return_value = {'embeddings': [[1, 2, 3]]}
        with patch('rag.requests.post', side_effect=[requests.ConnectionError(), response]) as post, patch('rag.recover_tunnel', return_value='https://new.free.pinggy.net') as repair:
            vector = OllamaClient('https://old.free.pinggy.net').embed(['test'])
            self.assertEqual(vector.shape, (1, 3))
            repair.assert_called_once_with('https://old.free.pinggy.net')
            self.assertEqual(post.call_count, 2)
            self.assertEqual(post.call_args_list[1].args[0], 'https://new.free.pinggy.net/api/embed')

    def test_read_timeout_does_not_duplicate_expensive_generation(self):
        with patch('rag.requests.post', side_effect=requests.ReadTimeout('sensitive URL')) as post, patch('rag.recover_tunnel') as repair:
            with self.assertRaises(RagError) as error:
                OllamaClient('https://old.free.pinggy.net').embed(['test'])
            self.assertEqual(error.exception.code, 'timeout')
            self.assertNotIn('sensitive', error.exception.public_message)
            post.assert_called_once()
            repair.assert_not_called()

    def test_recovery_is_bounded(self):
        with patch('rag.requests.post', side_effect=requests.ConnectionError()) as post, patch('rag.recover_tunnel', return_value='https://new.free.pinggy.net') as repair:
            with self.assertRaises(RagError):
                OllamaClient('https://old.free.pinggy.net').embed(['test'])
            self.assertEqual(post.call_count, 2)
            repair.assert_called_once()

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
