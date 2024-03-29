from apps.grabbo import tasks

import pytest


class MockDownloader(tasks.BaseDownloader):
    def download_companies(self) -> None:
        """No need to do anything here."""

    def download_jobs(self) -> None:
        """No need to do anything here."""


@pytest.mark.parametrize(
    'size_str, expected_size_from, expected_size_to',
    [
        ('1234-1235', 1234, 1235),
        ('1234 - 1235', 1234, 1235),
        ('1234+', 1234, 2468),
        ('10,000+', 10000, 20000),
        ('10,000+', 10000, 20000),
        ('500', 500, 500),
        ('+-80', 72, 88),
        ('<100', 0, 100),
        ('>100', 100, 200),
    ],
)
def test_parse_company_size(db, size_str, expected_size_from, expected_size_to):
    assert MockDownloader()._parse_company_size(size_str) == {
        'size_from': expected_size_from,
        'size_to': expected_size_to,
    }


def test_parse_company_size_invalid(db):
    with pytest.raises(ValueError):
        MockDownloader()._parse_company_size('1234 world-wide')
