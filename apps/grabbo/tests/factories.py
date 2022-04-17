import factory

from factory import fuzzy  # noqa: WPS458 (need to import fuzzy separately)


class CompanyFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('company')
    industry = fuzzy.FuzzyChoice(
        ['IT', 'Finance', 'Healthcare', 'Retail', 'Education', 'Other'],
    )
    size_from = fuzzy.FuzzyInteger(1, 100)
    size_to = fuzzy.FuzzyInteger(1, 100)
    url = factory.Faker('url')

    class Meta:
        model = 'grabbo.Company'
