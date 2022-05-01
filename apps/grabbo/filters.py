from django.contrib import admin
from django.db import models

from apps.grabbo.models import Job


class InputFilter(admin.SimpleListFilter):
    """
    A direct copy-paste of a thing found online.

    https://hakibenita.com/how-to-add-a-text-filter-to-django-admin
    """

    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        return ((), )

    def choices(self, changelist):
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (param_name, param_val)
            for param_name, param_val in changelist.get_filters_params().items()
            if param_name != self.parameter_name
        )
        yield all_choice


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


class SalaryFilter(InputFilter):
    parameter_name = 'min_salary'
    title = 'min_salary'

    def queryset(self, request, queryset):
        if self.value() is not None:
            min_salary = self.value()

            return queryset.filter(
                salary__amount_to__gte=min_salary,
            )
