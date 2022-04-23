from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.urls import reverse

from apps.grabbo.models import Company

import pytest


@pytest.mark.django_db
class TestCompanyDeduplicate:

    def test_deduplication_removes_company_with_same_name(
        self,
        admin_client,
        company_factory,
    ):
        companies = company_factory.create_batch(2, name='Fake Company')
        url = reverse('admin:grabbo_company_changelist')
        admin_client.post(
            url,
            data={
                'action': 'deduplicate',
                ACTION_CHECKBOX_NAME: [company.id for company in companies],
            },
        )
        assert Company.objects.count() == 1

    def test_deduplication_removes_company_with_similar_name(
        self,
        admin_client,
        company_factory,
    ):
        company_factory(name='Fake Company')
        company_long = company_factory(name='Fake Company sp. z o.o.')
        url = reverse('admin:grabbo_company_changelist')
        admin_client.post(
            url,
            data={
                'action': 'deduplicate',
                ACTION_CHECKBOX_NAME: [company_long.id],
            },
        )
        assert Company.objects.count() == 1

    @pytest.mark.parametrize(
        'company1_name, company2_name',
        [
            ('Fake Company', 'Another Fake Company sp. z o.o.'),
            ('Fake Company', 'Another Fake Company'),
            ('Fake Company sp. z o.o.', 'Another Fake Company'),
        ],
    )
    def test_deduplication_doesnt_remove_company_with_different_name(
        self,
        admin_client,
        company_factory,
        company1_name,
        company2_name,
    ):
        company_factory(name=company1_name)
        company2 = company_factory(name=company2_name)
        url = reverse('admin:grabbo_company_changelist')
        admin_client.post(
            url,
            data={
                'action': 'deduplicate',
                ACTION_CHECKBOX_NAME: [company2.id],
            },
        )
        assert Company.objects.count() == 2

    def test_deduplication_calls_update_if_better_if_the_match_exists(
        self,
        admin_client,
        company_factory,
        mocker,
    ):
        patched_update = mocker.patch('apps.grabbo.models.Company.update_if_better')
        company_factory(name='Fake Company')
        company_long = company_factory(name='Fake Company sp. z o.o.')
        url = reverse('admin:grabbo_company_changelist')
        admin_client.post(
            url,
            data={
                'action': 'deduplicate',
                ACTION_CHECKBOX_NAME: [company_long.id],
            },
        )
        assert patched_update.called
