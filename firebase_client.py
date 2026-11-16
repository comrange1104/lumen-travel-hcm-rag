"""Email/password REST authentication, adapted from the instructor's Lab 3.

Only Firebase Authentication is used. No Firestore, Admin SDK or service key.
"""
import time
import requests
from config import FIREBASE_API_KEY, FIREBASE_PROJECT_ID


class FirebaseError(Exception):
    pass


ERRORS = {
    'EMAIL_EXISTS': 'Email này đã được đăng ký. Hãy chuyển sang Đăng nhập.',
    'INVALID_LOGIN_CREDENTIALS': 'Email hoặc mật khẩu chưa đúng.',
    'INVALID_PASSWORD': 'Email hoặc mật khẩu chưa đúng.',
    'EMAIL_NOT_FOUND': 'Email hoặc mật khẩu chưa đúng.',
    'INVALID_EMAIL': 'Địa chỉ email chưa hợp lệ.',
    'WEAK_PASSWORD': 'Mật khẩu cần ít nhất 6 ký tự.',
    'OPERATION_NOT_ALLOWED': 'Hãy bật Email/Password trong Firebase Authentication.',
    'TOO_MANY_ATTEMPTS_TRY_LATER': 'Có quá nhiều lần thử. Hãy thử lại sau.',
    'USER_DISABLED': 'Tài khoản này đã bị vô hiệu hóa.',
}


def _request(url, **kwargs):
    if not FIREBASE_API_KEY or not FIREBASE_PROJECT_ID:
        raise FirebaseError('Chưa cấu hình Firebase. Xem hướng dẫn docs/FIREBASE_SETUP.md.')
    try:
        response = requests.post(url, params={'key': FIREBASE_API_KEY}, timeout=(10, 20), **kwargs)
        data = response.json()
    except (requests.RequestException, ValueError):
        raise FirebaseError('Không kết nối được Firebase. Kiểm tra Internet và cấu hình.') from None
    if not response.ok:
        code = str(data.get('error', {}).get('message', '')).split(' : ')[0]
        raise FirebaseError(ERRORS.get(code, 'Firebase từ chối yêu cầu. Kiểm tra cấu hình hoặc đăng nhập lại.'))
    return data


def sign_up(email, password):
    _credentials(email, password)
    _request('https://identitytoolkit.googleapis.com/v1/accounts:signUp',
             json={'email': email.strip(), 'password': password, 'returnSecureToken': True})


def sign_in(email, password):
    _credentials(email, password)
    data = _request('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword',
                    json={'email': email.strip(), 'password': password, 'returnSecureToken': True})
    return {'uid': data['localId'], 'email': data['email'], 'id_token': data['idToken'],
            'refresh_token': data['refreshToken'], 'expires_at': time.time() + int(data['expiresIn'])}


def _credentials(email, password):
    if not email.strip() or not password:
        raise FirebaseError('Vui lòng nhập email và mật khẩu.')


def refresh_user(user):
    if time.time() < user['expires_at'] - 60:
        return user
    data = _request('https://securetoken.googleapis.com/v1/token',
                    data={'grant_type': 'refresh_token', 'refresh_token': user['refresh_token']})
    return {**user, 'id_token': data['id_token'], 'refresh_token': data['refresh_token'],
            'expires_at': time.time() + int(data['expires_in'])}
