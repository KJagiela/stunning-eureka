from django.contrib import admin
from django.db import models

from apps.grabbo.models import (
    Job,
    JobSalary,
)


class CompanySizeFilter(admin.SimpleListFilter):
    title = 'company size'
    parameter_name = 'company_size'

    def lookups(self, request, model_admin):
        return (
            ('<100', 'up to 100'),
            ('101-200', 'up to 200'),
            ('201-500', 'up to 500'),
            ('501-1000', 'up to 1000'),
            ('>1000', 'giants'),
        )

    def queryset(self, request, queryset):
        if self.value() == '<100':
            return queryset.filter(company__size_from__lte=100)
        if self.value() == '101-200':
            return queryset.filter(
                company__size_from__gte=101,
                company__size_from__lte=200,
            )
        if self.value() == '201-500':
            return queryset.filter(
                company__size_from__gte=201,
                company__size_from__lte=500,
            )
        if self.value() == '501-1000':
            return queryset.filter(
                company__size_from__gte=501,
                company__size_from__lte=1000,
            )
        if self.value() == '>1000':
            return queryset.filter(company__size_from__gte=1001)


class TechnologyFilter(admin.SimpleListFilter):
    title = 'technology'
    parameter_name = 'technology'

    def lookups(self, request, model_admin):
        return [('python', 'python')]

    def queryset(self, request, queryset):
        if self.value() == 'python':
            return queryset.filter(
                models.Q(technology__name__icontains='python')
                | models.Q(technology__name__icontains='django'),
            )
        return queryset


class SeniorityFilter(admin.SimpleListFilter):
    title = 'seniority'
    parameter_name = 'seniority'

    def lookups(self, request, model_admin):
        seniorities = set(Job.objects.all().values_list('seniority', flat=True))
        return [(seniority, seniority) for seniority in seniorities]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(seniority=self.value())
        return queryset


class SalaryFilter(admin.SimpleListFilter):
    title = 'salary'
    parameter_name = 'salary'

    def lookups(self, request, model_admin):
        salaries = JobSalary.objects.aggregate(
            minimal=models.Min('amount_from'),
            maximal=models.Max('amount_to'),
        )
        no_of_buckets = 10
        step = (salaries['maximal'] - salaries['minimal']) / no_of_buckets
        return [
            f'{bucket * step}-{(bucket + 1) * step}'
            for bucket in range(no_of_buckets)
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(seniority=self.value())
        return queryset
