from django.conf import settings


def test_settings_load():
    assert settings.ROOT_URLCONF == "foodbudget_core.urls"
