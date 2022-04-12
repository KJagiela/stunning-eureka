from django.db import models

from apps.grabbo.managers import CompanyManager


class JobBoard(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255, blank=True)
    no_of_employees = models.CharField(max_length=32, default='', blank=True)
    url = models.CharField(max_length=1024, default='', blank=True)

    objects = CompanyManager()

    def __str__(self):
        return self.name


class JobLocation(models.Model):
    job = models.ForeignKey('grabbo.Job', on_delete=models.CASCADE)
    is_remote = models.BooleanField()
    is_covid_remote = models.BooleanField()
    city = models.CharField(max_length=32, null=True, blank=True)
    street = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f'{self.city}, {self.street}'


class JobCategory(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Technology(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class JobSalary(models.Model):
    amount_from = models.IntegerField()
    amount_to = models.IntegerField()
    amount_currency = models.CharField(max_length=4)
    job_type = models.CharField(max_length=32)

    def __str__(self):
        return f'{self.amount_from} - {self.amount_to} {self.amount_currency}'


class Job(models.Model):
    board = models.ForeignKey(
        'grabbo.JobBoard',
        on_delete=models.SET_NULL,
        null=True,
    )
    category = models.ForeignKey(
        'grabbo.JobCategory',
        on_delete=models.SET_NULL,
        null=True,
    )
    technology = models.ForeignKey(
        'grabbo.Technology',
        on_delete=models.SET_NULL,
        null=True,
    )
    salary = models.ForeignKey('grabbo.JobSalary', on_delete=models.PROTECT)
    original_id = models.CharField(max_length=256)
    company = models.ForeignKey('grabbo.Company', on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=256)
    url = models.CharField(max_length=256)

    def __str__(self):
        return f'{self.title} in {self.company}'
