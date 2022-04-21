import pytest

from apps.grabbo import tasks
from apps.grabbo.models import (
    Company,
    Job,
    JobCategory,
    JobLocation,
    JobSalary,
    Technology,
)


@pytest.fixture
def no_fluff(job_board_factory):
    return job_board_factory(name='nofluff')


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

    def test_job_board_property_returns_nofluff(self, no_fluff):
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
class TestNoFluffCompaniesHelpers:

    @pytest.fixture()
    def patched_spans(self, mocker):
        span1 = mocker.MagicMock()
        span1.string = 'Wielkość firmy'
        span1.next_sibling.string = '123-135'
        span2 = mocker.MagicMock()
        span2.string = 'Fake span'
        span2.next_sibling.string = '1' * 100
        span3 = mocker.MagicMock()
        span3.string = 'Branża'
        span3.next_sibling.string = 'it'
        span4 = mocker.MagicMock()
        span4.string = 'Branża'
        span4.next_sibling.string = 'marketing'
        return [span1, span2, span3, span4]

    def test_get_info_from_spans_returns_data_from_first_matching_span(
        self,
        patched_spans,
    ):
        assert tasks.NoFluffDownloader._get_info_from_spans(
            patched_spans,
            'Branża',
        ) == 'it'

    def test_get_info_returns_only_first_32_characters(  # noqa: WPS114
        self,
        patched_spans,
    ):
        assert tasks.NoFluffDownloader._get_info_from_spans(
            patched_spans,
            'Fake span',
        ) == '1' * 32

    def test_get_info_returns_empty_string_if_no_matching_span(
        self,
        patched_spans,
    ):
        assert tasks.NoFluffDownloader._get_info_from_spans(
            patched_spans,
            'name',
        ) == ''

    def test_scrap_company_page_returns_data_from_the_site(
        self,
        requests_mock,
        patched_spans,
        mocker,
    ):
        requests_mock.get('https://nofluffjobs.com/pl/company/1', text='')
        patched_soup = mocker.patch('apps.grabbo.tasks.BeautifulSoup')
        patched_find = patched_soup.return_value.find
        patched_find.return_value.find_all.return_value = patched_spans

        scrapped = tasks.NoFluffDownloader()._scrap_company_page({'url': '/company/1'})

        assert scrapped == {
            'url': 'https://nofluffjobs.com/pl/company/1',
            'size_from': 123,
            'size_to': 135,
            'industry': 'it',
        }


@pytest.mark.django_db
class TestNoFluffJobsDownloader:

    @pytest.fixture()
    def full_job_data(self):
        return {
            'category': 'it',
            'salary': {
                'from': '1000',
                'to': '2000',
                'type': 'hourly',
                'currency': 'PLN',
            },
            'name': 'Job 1',
            'technology': 'Python',
            'id': '1',
            'title': 'Job title',
            'url': 'https://example.com',
            'location': {
                'fullyRemote': False,
                'covidTimeRemotely': True,
                'places': [{
                    'city': 'Warsaw',
                    'street': 'Krakowska',
                }],
            },
        }

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

    def test_add_job_creates_category_if_didnt_exist(self, no_fluff, full_job_data):
        tasks.NoFluffDownloader()._add_job(full_job_data)
        assert JobCategory.objects.count() == 1
        assert JobCategory.objects.first().name == 'it'

    def test_add_job_creates_salary_object_from_data(self, no_fluff, full_job_data):
        tasks.NoFluffDownloader()._add_job(full_job_data)
        assert JobSalary.objects.count() == 1
        assert JobSalary.objects.first().amount_from == 1000

    def test_add_job_creates_company_if_didnt_exist(self, no_fluff, full_job_data):
        tasks.NoFluffDownloader()._add_job(full_job_data)
        assert Company.objects.count() == 1
        assert Company.objects.first().name == 'Job 1'

    def test_add_job_creates_technology_if_didnt_exist(self, no_fluff, full_job_data):
        tasks.NoFluffDownloader()._add_job(full_job_data)
        assert Technology.objects.count() == 1
        assert Technology.objects.first().name == 'Python'

    def test_add_job_creates_job_instance_with_appropriate_foreign_keys(
        self,
        no_fluff,
        full_job_data,
    ):
        tasks.NoFluffDownloader()._add_job(full_job_data)
        assert Job.objects.count() == 1
        job = Job.objects.first()
        assert job.category == JobCategory.objects.first()
        assert job.original_id == '1'

    def test_add_object_adds_locations_from_data(self, no_fluff, full_job_data):
        tasks.NoFluffDownloader()._add_job(full_job_data)
        assert JobLocation.objects.count() == 1
        assert JobLocation.objects.first().city == 'Warsaw'
