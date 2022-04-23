from apps.grabbo.managers import CompanyManager
from apps.grabbo.models import Company

import pytest


@pytest.mark.django_db
class TestCompanyManager:

    def test_get_possible_match_returns_companies_with_same_name(
        self,
        company_factory,
    ):
        company_factory.create_batch(2, name='Fake Company')
        manager = CompanyManager()
        manager.model = Company
        matches = manager.get_possible_match('Fake Company')
        assert matches.count() == 2

    @pytest.mark.parametrize(
        'company1_name, company2_name',
        [
            ('Fake Company', 'Fake Company sp. z o.o.'),
            ('Fake Company sp. z o.o.', 'Fake Company'),
            ('Fake Company sp. z o.o.', 'Fake Company sp. z o.o.'),
        ],
    )
    def test_get_possible_match_returns_companies_with_similar_name(
        self,
        company_factory,
        company1_name,
        company2_name,
    ):
        company_factory(name=company1_name)
        company_factory(name=company2_name)
        manager = CompanyManager()
        manager.model = Company
        matches = manager.get_possible_match(company1_name)
        assert matches.count() == 2

    @pytest.mark.parametrize(
        'company_name',
        ['Flake Company', 'Flakes Company sp. z o.o.', 'A Company'],
    )
    def test_get_possible_match_doesnt_return_companies_with_different_names(
        self,
        company_factory,
        company_name,
    ):
        company_factory(name=company_name)
        manager = CompanyManager()
        manager.model = Company
        matches = manager.get_possible_match('Fake Company')
        assert matches.count() == 0
