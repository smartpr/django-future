from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SECRET_KEY = "some-key"

INSTALLED_APPS = [
    "tests",
    'django.contrib.contenttypes',
    'django_future',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
