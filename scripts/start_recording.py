"""User-run Windows launcher. Restores services without saving passwords."""
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import webbrowser
import requests
from dotenv import dotenv_values, set_key

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT/'tmp'


def healthy(url):
    try:
        response = requests.get(url, timeout=(3, 5))
        return response.ok
    except requests.RequestException:
        return False


def start_hidden(command, name):
    return subprocess.Popen(command, cwd=ROOT,
                            stdout=(TMP/f'{name}.log').open('w', encoding='utf-8'),
                            stderr=(TMP/f'{name}-error.log').open('w', encoding='utf-8'),
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)


def ensure_services():
    TMP.mkdir(exist_ok=True)
    values = dotenv_values(ROOT/'.env')
    if not values.get('FIREBASE_API_KEY') or not values.get('FIREBASE_PROJECT_ID'):
        raise RuntimeError('Chưa cấu hình Firebase. Xem docs/FIREBASE_SETUP.md.')
    if not healthy('http://127.0.0.1:11434/api/tags'):
        executable = shutil.which('ollama') or str(Path(os.environ.get('LOCALAPPDATA', ''))/'Programs/Ollama/ollama.exe')
        if not Path(executable).exists():
            raise RuntimeError('Chưa tìm thấy Ollama. Cài Ollama và tải hai mô hình theo README.')
        print('Đang khởi động Ollama…', flush=True)
        start_hidden([executable, 'serve'], 'recording-ollama')
        for _ in range(40):
            if healthy('http://127.0.0.1:11434/api/tags'):
                break
            time.sleep(.5)
        else:
            raise RuntimeError('Ollama chưa sẵn sàng. Xem tmp/recording-ollama-error.log.')
    try:
        response = requests.get('http://127.0.0.1:11434/api/tags', timeout=10)
        models = {item['name'] for item in response.json()['models']}
    except (requests.RequestException, ValueError, KeyError):
        raise RuntimeError('Không đọc được danh sách mô hình Ollama.') from None
    if 'qwen3:4b' not in models or not any(m in ('embeddinggemma', 'embeddinggemma:latest') for m in models):
        raise RuntimeError('Cần tải mô hình: ollama pull embeddinggemma và ollama pull qwen3:4b.')
    base = (values.get('OLLAMA_BASE_URL') or '').rstrip('/')
    if not (base.startswith('https://') and healthy(base+'/api/tags')):
        print('Đang tạo lại tunnel Pinggy…', flush=True)
        key = TMP/'pinggy_key'
        if not key.exists():
            subprocess.run(['ssh-keygen', '-q', '-t', 'ed25519', '-f', str(key), '-N', ''], check=True)
        process = start_hidden(['ssh', '-tt', '-i', str(key), '-o', 'IdentitiesOnly=yes',
                                '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=accept-new',
                                '-o', 'ServerAliveInterval=30', '-p', '443',
                                '-R0:127.0.0.1:11434', 'free.pinggy.io', 'u:Host:localhost:11434'], 'recording-pinggy')
        for _ in range(45):
            log = (TMP/'recording-pinggy.log').read_text(encoding='utf-8', errors='replace')
            urls = re.findall(r'https://[a-z0-9-]+\.free\.pinggy\.net', log)
            if urls and healthy(urls[-1]+'/api/tags'):
                base = urls[-1]
                set_key(ROOT/'.env', 'OLLAMA_BASE_URL', base, quote_mode='never')
                break
            if process.poll() is not None:
                raise RuntimeError('Không mở được Pinggy. Xem tmp/recording-pinggy-error.log.')
            time.sleep(.5)
        else:
            raise RuntimeError('Pinggy chưa sẵn sàng. Chạy lại launcher hoặc kiểm tra Internet.')
    print('Firebase có cấu hình; Ollama và Pinggy đã kết nối.', flush=True)


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--port', type=int, default=8503)
    args = parser.parse_args()
    try:
        ensure_services()
        url = f'http://localhost:{args.port}'
        if healthy(url+'/_stcore/health'):
            print('Trang trình diễn đã chạy:', url)
            if not args.no_browser:
                webbrowser.open(url)
            return 0
        process = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run',
                                    str(ROOT/'record_demo.py'), '--server.port', str(args.port),
                                    '--server.headless', 'true'], cwd=ROOT)
        for _ in range(30):
            if healthy(url+'/_stcore/health'):
                break
            if process.poll() is not None:
                raise RuntimeError('Streamlit không khởi động được. Đọc thông báo phía trên.')
            time.sleep(.5)
        else:
            process.terminate()
            raise RuntimeError('Streamlit chưa sẵn sàng. Thử lại sau.')
        print('\nMở', url, flush=True)
        print('Đăng nhập thật → Chuẩn bị cẩm nang → Bắt đầu → bấm quay trong 8 giây.', flush=True)
        print('Giữ cửa sổ này mở trong lúc quay. Ctrl+C để dừng.', flush=True)
        if not args.no_browser:
            webbrowser.open(url)
        try:
            return process.wait()
        except KeyboardInterrupt:
            process.terminate()
            return 0
    except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print('Không thể chuẩn bị demo:', str(exc), flush=True)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
