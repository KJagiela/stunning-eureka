import pytest

from apps.grabbo import tasks
from apps.grabbo.models import Company


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
def test_parse_company_size(size_str, expected_size_from, expected_size_to):
    assert tasks.BaseDownloader._parse_company_size(size_str) == {
        'size_from': expected_size_from,
        'size_to': expected_size_to,
    }


@pytest.mark.django_db
class TestNoFluffCompaniesDownloader:

    @pytest.fixture()
    def companies_response(self, requests_mock, mocker):
        requests_mock.get(
            tasks.NoFluffDownloader.companies_url,
            json={'items': [
                {'id': 1, 'name': 'Company 1 sp. z o.o.'},
            ]},
        )
        mocker.patch(
            'apps.grabbo.tasks.NoFluffDownloader._scrap_company_page',
            return_value={
                'url': 'https://example.com',
                'size_from': 1234,
                'size_to': 1235,
                'industry': 'IT',
            },
        )

    def test_job_board_property_returns_nofluff(self, job_board_factory):
        no_fluff = job_board_factory(name='nofluff')
        assert tasks.NoFluffDownloader().job_board == no_fluff

    def test_download_companies_calls_api(self, requests_mock):
        patched_get = requests_mock.get(
            tasks.NoFluffDownloader.companies_url,
            json={'items': []},
        )
        tasks.NoFluffDownloader().download_companies()
        assert patched_get.called

    def test_download_companies_returns_early_if_api_returns_error(
        self,
        requests_mock,
        mocker,
    ):
        requests_mock.get(
            tasks.NoFluffDownloader.companies_url,
            status_code=500,
        )
        patched_logger = mocker.patch('apps.grabbo.tasks.logger.error')

        tasks.NoFluffDownloader().download_companies()
        assert patched_logger.called

    def test_download_companies_adds_company_if_it_doesnt_already_exist(
        self,
        companies_response,
    ):
        assert Company.objects.count() == 0
        tasks.NoFluffDownloader().download_companies()
        assert Company.objects.count() == 1
        assert Company.objects.first().name == 'Company 1'

    def test_download_companies_updates_company_if_it_already_exists(
        self,
        companies_response,
        company_factory,
    ):
        company_factory(name='Company 1', size_from=0)
        tasks.NoFluffDownloader().download_companies()
        assert Company.objects.first().size_from == 1234


@pytest.mark.django_db
class TestNoFluffJobsDownloader:

    def test_download_jobs_logs_error_if_api_returned_error(
        self,
        requests_mock,
        mocker,
    ):
        requests_mock.post(tasks.NoFluffDownloader.jobs_url, status_code=500)
        patched_logger = mocker.patch('apps.grabbo.tasks.logger.error')
        tasks.NoFluffDownloader().download_jobs()
        assert patched_logger.called

    def test_download_jobs_adds_job_if_it_doesnt_already_exist(
        self,
        requests_mock,
        mocker,
    ):
        requests_mock.post(
            tasks.NoFluffDownloader.jobs_url,
            json={'postings': [{'id': 1, 'title': 'Job 1'}]},
        )
        patched_add_job = mocker.patch('apps.grabbo.tasks.NoFluffDownloader._add_job')
        tasks.NoFluffDownloader().download_jobs()
        assert patched_add_job.called

    def test_download_jobs_ignores_job_if_it_already_exists(
        self,
        requests_mock,
        mocker,
        job,
    ):
        requests_mock.post(
            tasks.NoFluffDownloader.jobs_url,
            json={'postings': [{'id': job.original_id, 'title': 'Job 1'}]},
        )
        patched_add_job = mocker.patch('apps.grabbo.tasks.NoFluffDownloader._add_job')
        tasks.NoFluffDownloader().download_jobs()
        assert not patched_add_job.called
