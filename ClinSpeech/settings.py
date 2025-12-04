"""
Django settings for ClinSpeech project.
"""
import os
from pathlib import Path
import environ  # Библиотека для работы с .env файлами

# 1. Инициализация переменных окружения
env = environ.Env()
# Читаем файл .env, который должен лежать рядом с manage.py
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# 2. Безопасность (берем из файла .env)
SECRET_KEY = env('SECRET_KEY', default='django-insecure-fallback-key')
DEBUG = env.bool('DEBUG', default=True)

# Разрешенные хосты (берем списком из .env или ставим по умолчанию локальные)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost'])

# 3. Приложения
INSTALLED_APPS = [
    'django_q',  # django-q2 импортируется как django_q
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS должен быть вверху
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ClinSpeech.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ClinSpeech.wsgi.application'

# 4. База данных (Берет настройки из .env)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'OPTIONS': {
            # Путь к SSL сертификату (ca.pem должен лежать рядом с manage.py)
            'ssl': {'ca': os.path.join(BASE_DIR, 'ca.pem')},

            # ВАЖНО: Добавили отключение проверки Primary Key
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES', sql_require_primary_key = 0"
        },
    }
}

# 5. Пароли
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 6. Локализация
LANGUAGE_CODE = 'ru-ru'  # Поставил русский, раз проект для нас
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 7. Статика и Медиа
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 8. Дополнительные настройки
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Наша кастомная модель пользователя
AUTH_USER_MODEL = 'api.User'

# Разрешаем запросы с любых доменов (для разработки)
CORS_ALLOW_ALL_ORIGINS = True

Q_CLUSTER = {
    'name': 'ClinSpeech_Cluster',
    'workers': 2,        # Количество потоков
    'recycle': 500,
    'timeout': 600,      # Время на одну задачу (10 минут, хватит для Whisper)
    'retry': 700,        # retry должен быть больше timeout
    'compress': True,
    'save_limit': 250,
    'queue_limit': 500,
    'cpu_affinity': 1,
    'label': 'Django Q',
    'orm': 'default'   }