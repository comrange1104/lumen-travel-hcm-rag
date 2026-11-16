"""Recover only the configured Pinggy transport; never substitute local answers."""
import logging
import threading
from urllib.parse import urlparse
from dotenv import dotenv_values
from config import ROOT

_LOCK = threading.Lock()
logger = logging.getLogger('lumen.connection')


class ConnectionSetupError(Exception):
    @property
    def public_message(self):
        return str(self)


def is_pinggy_url(url):
    host = (urlparse(url).hostname or '').lower()
    return any(host.endswith(suffix) for suffix in ('.pinggy.net', '.pinggy-free.link', '.pinggy.link'))


def recover_tunnel(failed_url):
    if not is_pinggy_url(failed_url):
        raise ConnectionSetupError('URL này không phải tunnel Pinggy của ứng dụng.')
    from scripts.start_recording import ensure_services, healthy
    with _LOCK:
        current = (dotenv_values(ROOT/'.env').get('OLLAMA_BASE_URL') or '').rstrip('/')
        if is_pinggy_url(current) and current != failed_url and healthy(current+'/api/tags'):
            return current
        try:
            return ensure_services(verbose=False)
        except Exception:
            logger.exception('Pinggy recovery failed')
            raise ConnectionSetupError('Không khôi phục được kết nối Pinggy. Mở QUAY_DEMO.bat để kiểm tra dịch vụ và Internet.') from None


def ensure_connection(base_url):
    from scripts.start_recording import healthy
    if healthy(base_url.rstrip('/')+'/api/tags'):
        return base_url.rstrip('/')
    if is_pinggy_url(base_url):
        return recover_tunnel(base_url)
    raise ConnectionSetupError('Không kết nối được địa chỉ Ollama đã cấu hình.')
