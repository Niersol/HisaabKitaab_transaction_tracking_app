from .common import *
DEBUG = True
ALLOWED_HOSTS = ['*']
SECRET_KEY = 'django-insecure-*(ex1m!q^a5!)hk&l=ixu)#&j=-*p1-yn(j^2r+_79%ne4)m(&'
DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "accounts_2",
        "USER": "postgres",
        "PASSWORD": "45645688mm",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]