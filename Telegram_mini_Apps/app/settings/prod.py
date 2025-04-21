from .base import *


DEBUG = False

ADMINS = [
('admins', 'admin'),
]


CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False

ALLOWED_HOSTS = ['your_domen', 'www.your_domen']
X_FRAME_OPTIONS = 'ALLOW'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}