from django.conf import settings

urlpatterns = []

settings.configure(
    DATABASES={
        'default': {
            'NAME': 'test_db',
            'ENGINE': 'django.db.backends.sqlite3'
        }
    },
    ROOT_URLCONF=__name__,
    INSTALLED_APPS=[],
    DEFAULT_INDEX_TABLESPACE='',
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'builtins': ['django_helpers.builtins']
            },
        },
    ]
)

import django
django.setup()
