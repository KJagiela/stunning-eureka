import pytest

from pytest_factoryboy import register

from apps.grabbo.tests.factories import CompanyFactory

register(CompanyFactory)


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath
