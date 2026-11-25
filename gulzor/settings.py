import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env():
    """Oddiy .env o'qigich (qo'shimcha kutubxonasiz). Format: KEY=VALUE"""
    env_file = BASE_DIR / '.env'
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env()

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-productionda-almashtiring')
DEBUG = os.environ.get('DEBUG', '0' if os.environ.get('RENDER') else '1') == '1'
ALLOWED_HOSTS = ['*'] if DEBUG else [h for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h]
render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if render_host:
    ALLOWED_HOSTS.append(render_host)
    CSRF_TRUSTED_ORIGINS = [f'https://{render_host}']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gulzor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gulzor.wsgi.application'
ASGI_APPLICATION = 'gulzor.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/admin/login/'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30

# ---------- Ro'yxatdan o'tish: Google + telefon (SMS kod) ----------
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')

# SMS provayder: Eskiz.uz (https://eskiz.uz). Kalitlar bo'lmasa kod terminalga chiqadi.
ESKIZ_EMAIL = os.environ.get('ESKIZ_EMAIL', '')
ESKIZ_PASSWORD = os.environ.get('ESKIZ_PASSWORD', '')
ESKIZ_FROM = os.environ.get('ESKIZ_FROM', '4546')
SMS_CONFIGURED = bool(ESKIZ_EMAIL and ESKIZ_PASSWORD)

# Faqat local sinov uchun: SMS sozlanmagan bo'lsa, kod oynada ham ko'rsatiladi.
SHOW_DEV_CODE = DEBUG and not SMS_CONFIGURED

OTP_TTL_SECONDS = 300      # kod 5 daqiqa amal qiladi
OTP_RESEND_SECONDS = 60    # qayta yuborish oralig'i
OTP_MAX_ATTEMPTS = 5       # noto'g'ri kiritish urinishlari
