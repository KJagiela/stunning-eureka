from copy import copy

from apps.grabbo import tasks
from apps.grabbo.models import (
    Company,
    Job,
    JobCategory,
    JobLocation,
    JobSalary,
    Technology,
)

import pytest


@pytest.fixture
def just_join_it(job_board_factory):
    return job_board_factory(name='justjoin.it')


@pytest.fixture()
def full_job_data():
    return {
        'marker_icon': 'it',
        'employment_types': [
            {
                'salary': {
                    'from': '1000',
                    'to': '2000',
                    'currency': 'PLN',
                },
                'type': 'hourly',
            },
        ],
        'company_name': 'Job 1',
        'company_size': '1-10',
        'company_url': 'https://example.com',
        'id': '1',
        'title': 'Job title',
        'workplace_type': 'remote',
        'remote_interview': False,
        'technology': 'Python',
        'city': 'Warsaw',
        'street': 'Krakowska',
        'experience_level': 'junior',
    }


@pytest.mark.django_db
class TestJustJoinItJobsDownloader:

    def test_download_jobs_logs_error_if_api_returned_error(
        self,
        requests_mock,
        mocker,
    ):
        requests_mock.get(tasks.JustJoinItDownloader.jobs_url, status_code=500)
        patched_logger = mocker.patch('apps.grabbo.tasks.logger.error')
        tasks.JustJoinItDownloader().download_jobs()
        assert patched_logger.called

    def test_download_jobs_adds_job_if_it_doesnt_already_exist(
        self,
        requests_mock,
        mocker,
    ):
        requests_mock.get(
            tasks.JustJoinItDownloader.jobs_url,
            json=[{'id': 1, 'title': 'Job 1'}],
        )
        patched_add_job = mocker.patch(
            'apps.grabbo.tasks.JustJoinItDownloader._add_job',
        )
        tasks.JustJoinItDownloader().download_jobs()
        assert patched_add_job.called

    def test_download_jobs_ignores_job_if_it_already_exists(
        self,
        requests_mock,
        mocker,
        job,
    ):
        requests_mock.get(
            tasks.JustJoinItDownloader.jobs_url,
            json=[{'id': job.original_id, 'title': 'Job 1'}],
        )
        patched_add_job = mocker.patch(
            'apps.grabbo.tasks.JustJoinItDownloader._add_job',
        )
        tasks.JustJoinItDownloader().download_jobs()
        assert not patched_add_job.called

    def test_add_job_skips_jobs_without_salaries(self, full_job_data):
        data_no_salary = [{'salary': None, 'type': 'hourly'}]
        job_without_salary = copy(full_job_data)
        job_without_salary['employment_types'] = data_no_salary
        tasks.JustJoinItDownloader()._add_job(job_without_salary)
        assert Job.objects.count() == 0

    def test_add_job_creates_category_if_didnt_exist(self, just_join_it, full_job_data):
        tasks.JustJoinItDownloader()._add_job(full_job_data)
        assert JobCategory.objects.count() == 1
        assert JobCategory.objects.first().name == 'it'

    def test_add_job_creates_salary_object_from_data(self, just_join_it, full_job_data):
        tasks.JustJoinItDownloader()._add_job(full_job_data)
        assert JobSalary.objects.count() == 1
        assert JobSalary.objects.first().amount_from == 1000

    def test_add_job_creates_company_if_didnt_exist(self, just_join_it, full_job_data):
        tasks.JustJoinItDownloader()._add_job(full_job_data)
        assert Company.objects.count() == 1
        assert Company.objects.first().name == 'Job 1'

    def test_add_job_creates_technology_if_didnt_exist(
        self,
        just_join_it,
        full_job_data,
    ):
        tasks.JustJoinItDownloader()._add_job(full_job_data)
        assert Technology.objects.count() == 1
        assert Technology.objects.first().name == 'it'

    def test_add_job_creates_job_instance_with_appropriate_foreign_keys(
        self,
        just_join_it,
        full_job_data,
    ):
        tasks.JustJoinItDownloader()._add_job(full_job_data)
        assert Job.objects.count() == 1
        job = Job.objects.first()
        assert job.category == JobCategory.objects.first()
        assert job.original_id == '1'

    def test_add_object_adds_locations_from_data(self, just_join_it, full_job_data):
        tasks.JustJoinItDownloader()._add_job(full_job_data)
        assert JobLocation.objects.count() == 1
        assert JobLocation.objects.first().city == 'Warsaw'


@pytest.mark.django_db
class TestNoFluffCompaniesHelpers:

    def test_add_or_update_company_adds_company_if_it_doesnt_already_exist(
        self,
        full_job_data,
    ):
        assert Company.objects.count() == 0
        tasks.JustJoinItDownloader()._add_or_update_company(full_job_data)
        assert Company.objects.count() == 1
        assert Company.objects.first().name == 'Job 1'

    def test_add_or_update_company_updates_company_if_it_already_exists(
        self,
        full_job_data,
        company_factory,
    ):
        company_factory(name='Job 1', size_from=0)
        tasks.JustJoinItDownloader()._add_or_update_company(full_job_data)
        assert Company.objects.first().size_from == 1
