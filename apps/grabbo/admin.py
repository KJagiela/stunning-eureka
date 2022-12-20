from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from .filters import (
    CompanySizeFilter,
    SalaryFilter,
    SeniorityFilter,
    TechnologyFilter,
)
from .models import (
    Company,
    Job,
    JobBoard,
    JobCategory,
    JobLocation,
    JobSalary,
    Technology,
)
from .tasks import download_jobs


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'company',
        'company_size',
        'board',
        'category',
        'salary',
        'original_url',
    )
    list_filter = (CompanySizeFilter, SeniorityFilter, TechnologyFilter, SalaryFilter)
    actions = ('fix_nofluff_links',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('salary', 'category', 'board', 'company')

    @admin.display(description='Salary')
    def salary(self, obj):
        return f'{obj.salary.amount_from} - {obj.salary.amount_to}'

    @admin.display(description='Company size')
    def company_size(self, obj):
        return f'{obj.company.size_from} - {obj.company.size_to}'

    @admin.display(description='Original URL')
    def original_url(self, obj):
        return format_html('<a href="{0}" target="_blank">{1}</a>', obj.url, obj.url)


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
    actions = ('download_jobs',)

    @admin.action(description='Download jobs')
    def download_jobs(self, request: HttpRequest, queryset: QuerySet[JobBoard]) -> None:
        for board in queryset:
            download_jobs.delay(board.name)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'size_from', 'size_to', 'url')
    actions = ('deduplicate',)

    @admin.action(description='Deduplicate companies')
    def deduplicate(self, request: HttpRequest, queryset: QuerySet[Company]) -> None:
        for company in queryset:
            duplicated_companies = (
                Company.objects.get_possible_match(company.name).exclude(pk=company.pk)
            )
            if duplicated_companies.exists():
                duplicated_company = duplicated_companies.first()
                company.update_if_better(
                    industry=duplicated_company.industry,
                    size_from=duplicated_company.size_from,
                    size_to=duplicated_company.size_to,
                    url=duplicated_company.url,
                )
                duplicated_company.delete()
