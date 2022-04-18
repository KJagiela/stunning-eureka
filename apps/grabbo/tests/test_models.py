import pytest

from apps.grabbo.models import Company


@pytest.mark.django_db
class TestModelStrings:
    def test_job_board_string(self, job_board):
        assert str(job_board) == job_board.name

    def test_company_str(self, company):
        assert str(company) == company.name

    def test_job_location_str(self, job_location):
        assert str(job_location) == f'{job_location.city}, {job_location.street}'

    def test_job_category_str(self, job_category):
        assert str(job_category) == job_category.name

    def test_technology_str(self, technology):
        assert str(technology) == technology.name

    def test_job_salary_str(self, job_salary):
        assert str(job_salary) == (
            f'{job_salary.amount_from} - {job_salary.amount_to} {job_salary.currency}'
        )

    def test_job_str(self, job):
        assert str(job) == f'{job.title} in {job.company}'


@pytest.mark.django_db
class TestCompanyUpdateIfBetter:
    @pytest.mark.parametrize(
        'field_name, empty_value, better_value',
        [
            ('industry', '', 'IT'),
            ('industry', '', ''),
            ('size_from', 0, 100),
            ('size_from', 0, 0),
            ('size_to', 0, 100),
            ('size_to', 0, 0),
            ('url', '', 'https://www.google.com'),
            ('url', '', ''),
        ],
    )
    def test_update_if_better_sets_field_if_was_null(
        self,
        company_factory,
        field_name,
        empty_value,
        better_value,
    ):
        company = company_factory(**{field_name: empty_value})
        company.update_if_better(**{field_name: better_value})
        assert getattr(Company.objects.get(id=company.id), field_name) == better_value

    @pytest.mark.parametrize(
        'field_name, current_value, better_value',
        [
            ('industry', 'IT', 'Marketing'),
            ('industry', 'IT', ''),
            ('size_from', 100, 1000),
            ('size_from', 100, 0),
            ('size_to', 100, 1000),
            ('size_to', 100, 0),
            ('url', 'https://www.google.com', 'https://www.example.com'),
            ('url', 'https://www.google.com', ''),
        ],
    )
    def test_update_if_better_does_not_set_field_if_was_not_null(
        self,
        company_factory,
        field_name,
        current_value,
        better_value,
    ):
        company = company_factory(**{field_name: current_value})
        company.update_if_better(**{field_name: better_value})
        assert getattr(Company.objects.get(id=company.id), field_name) == current_value
