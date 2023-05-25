from apps.grabbo.models import Job

from rest_framework import serializers


class JobSerializer(serializers.ModelSerializer):
    salary = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name')
    category = serializers.CharField(source='category.name')
    technology = serializers.CharField(source='technology.name')
    company_size = serializers.SerializerMethodField()
    company_id = serializers.IntegerField(source='company.id')

    class Meta:
        model = Job
        fields = (
            'id',
            'company_id',
            'category',
            'technology',
            'salary',
            'seniority',
            'company_name',
            'title',
            'description',
            'company_size',
            'url',
        )

    def get_company_size(self, job):
        company = job.company
        return f'{company.size_from}-{company.size_to}'

    def get_salary(self, job):
        amount_from = job.salary.amount_from
        amount_to = job.salary.amount_to
        currency = job.salary.currency
        return f'{amount_from}-{amount_to} {currency}'
