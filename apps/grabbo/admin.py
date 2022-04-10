from django.contrib import admin

from .models import (
    Company,
    Job,
    JobBoard,
    JobCategory,
    JobLocation,
    JobSalary,
    Technology,
)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'company',
        'company_size',
        'board',
        'category',
        'salary_from',
        'salary_to',
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('salary', 'category')

    @admin.display(description='Salary min')
    def salary_from(self, obj):
        return obj.salary.amount_from

    @admin.display(description='Salary max')
    def salary_to(self, obj):
        return obj.salary.amount_to

    @admin.display(description='Company size')
    def company_size(self, obj):
        return obj.company.no_of_employees


@admin.register(JobSalary)
class JobSalaryAdmin(admin.ModelAdmin):
    """Register JobSalary model in admin panel."""


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    """Register Technology model in admin panel."""


@admin.register(JobLocation)
class JobLocationAdmin(admin.ModelAdmin):
    """Register JobLocation model in admin panel."""


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    """Register JobCategory model in admin panel."""


@admin.register(JobBoard)
class JobBoardAdmin(admin.ModelAdmin):
    """Register JobBoard model in admin panel."""


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Register Company model in admin panel."""
