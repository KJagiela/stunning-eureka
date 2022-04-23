import logging

from abc import ABC
from functools import cached_property
from typing import Union

import requests

from bs4 import BeautifulSoup
from tqdm import tqdm

from .models import (
    Company,
    Job,
    JobBoard,
    JobCategory,
    JobLocation,
    JobSalary,
    Technology,
)

logger = logging.getLogger(__name__)

ResponseDictKeys = Union[str, dict[str, str]]
ResponseList = list[dict[str, str]]
NestedResponseDict = dict[str, ResponseDictKeys]
ResponseWithList = dict[str, Union[str, ResponseList]]


class BaseDownloader(ABC):
    companies_url: str = ''
    jobs_url: str = ''

    def download(self) -> None:
        self.download_companies()
        self.download_jobs()

    def download_companies(self) -> None:
        # TODO: private method
        raise NotImplementedError('You must implement this method')

    def download_jobs(self) -> None:
        raise NotImplementedError('You must implement this method')

    def _parse_company_size(self, size: str) -> dict[str, int]:  # noqa: WPS210, WPS212
        """
        Parse company size from string to a pair of ints.

        There is no unified way the size is represented, so we need to check
        which type of size it is.

        Ignores are: too many variables, too many return statements.
        But since this method only parses the size, it can have as many returns
        and variables as it likes.
        """
        # TODO: class method?
        # TODO: bump to 10 and pattern match? :>
        chars_to_remove = {',', ' ', '.', "'"}
        for char in chars_to_remove:
            size = size.replace(char, '')
        try:
            size_exact = int(size)
        except ValueError:
            # If not a number, we assume it's a range.
            pass  # noqa: WPS420 - no consequences if it's not a number
        else:
            return {
                'size_from': size_exact,
                'size_to': size_exact,
            }
        if '+-' in size:
            size_approximate = int(size.strip('+-').strip())
            return {
                'size_from': int(size_approximate * 0.9),  # noqa: WPS432 magic number
                'size_to': int(size_approximate * 1.1),  # noqa: WPS432 magic number
            }
        if '-' in size:
            split_size = size.split('-')
            return {
                'size_from': int(split_size[0].strip()),
                'size_to': int(split_size[1].strip()),
            }
        if '+' in size:
            size_from = int(size.strip('+').strip())
            return {
                'size_from': size_from,
                'size_to': 2 * size_from,
            }
        if '<' in size:
            return {
                'size_from': 0,
                'size_to': int(size.strip('<').strip()),
            }
        if '>' in size:
            size_from = int(size.strip('>').strip())
            return {
                'size_from': size_from,
                'size_to': 2 * size_from,
            }
        if '(' in size:
            real_size = size.split('(')[0]
            return self._parse_company_size(real_size)
        logger.error(f'Unknown size: {size}')
        return {
            'size_from': 0,
            'size_to': 0,
        }


class NoFluffDownloader(BaseDownloader):
    companies_url = (
        'https://nofluffjobs.com/api/companies/search/all?'
        + 'salaryCurrency=PLN&salaryPeriod=month&region=pl'
    )
    jobs_url = (
        'https://nofluffjobs.com/api/search/posting?'
        + 'limit=40000&offset=0&salaryCurrency=PLN&salaryPeriod=month&region=pl'
    )

    @cached_property
    def job_board(self) -> JobBoard:
        return JobBoard.objects.get(name='nofluff')

    def download_companies(self) -> None:
        response = requests.get(self.companies_url)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            logger.error('Whoops, couldnt get companies from nofluff.')
            return

        resp_data = response.json()
        for company in tqdm(resp_data['items']):
            possible_companies = Company.objects.get_possible_match(
                name=company['name'],
            )
            # if 0 or more than 1 possible matches, we create a new company
            # if there's more than 1, we can't be sure that this is the same one,
            # so we create a new company
            if possible_companies.count() == 1:
                continue
            additional_company_data = self._scrap_company_page(company)
            Company.objects.create(
                name=company['name'].replace('sp. z o.o.', '').strip(),
                **additional_company_data,
            )

    def download_jobs(self) -> None:
        response = requests.post(
            self.jobs_url,
            json={'criteriaSearch': {}, 'page': 1},
        )
        try:
            response.raise_for_status()
        except requests.HTTPError:
            logger.error('Whoops, couldnt get offers from NoFluff.')
            return
        jobs = response.json()
        for job in tqdm(jobs['postings']):
            if Job.objects.filter(original_id=job['id']).exists():
                continue
            self._add_job(job)

    @staticmethod
    def _get_info_from_spans(spans: list, key_to_find: str) -> str:
        matching_spans = [span for span in spans if key_to_find in span.string]
        try:
            # only first 32 chars because this is our max
            return matching_spans[0].next_sibling.string[:32]  # noqa: WPS432
        except IndexError:
            return ''

    def _scrap_company_page(self, company: dict[str, str]) -> dict[str, str]:
        url = f'https://nofluffjobs.com/pl{company["url"]}'
        company_resp = requests.get(url)
        company_data = BeautifulSoup(company_resp.content, 'html.parser')
        spans = company_data.find(id='company-main').find_all('span')
        size = self._get_info_from_spans(spans, 'Wielkość firmy')
        return {
            'url': url,
            'industry': self._get_info_from_spans(spans, 'Branża'),
            **self._parse_company_size(size),
        }

    def _add_job(self, job: NestedResponseDict) -> None:
        category, _ = JobCategory.objects.get_or_create(name=job['category'])
        salary = self._add_salary(job['salary'])
        try:
            company, _ = Company.objects.get_or_create(
                name=job['name'],
                defaults={'size_from': 0, 'size_to': 0, 'url': ''},
            )
        except Company.MultipleObjectsReturned:
            logger.debug(job['name'])
            company = Company.objects.filter(name=job['name']).first()
        technology, _ = Technology.objects.get_or_create(
            name=job.get('technology', 'Unknown'),
        )
        job_instance = Job.objects.create(
            original_id=job['id'],
            board=self.job_board,
            category=category,
            technology=technology,
            salary=salary,
            company=company,
            seniority=job['seniority'][0].lower(),
            title=job['title'],
            url=job['url'],
        )
        self._add_locations(job_instance, job['location'])

    @staticmethod
    def _add_locations(job_instance: Job, location_entries: ResponseWithList) -> None:
        is_remote = location_entries['fullyRemote']
        is_covid_remote = location_entries['covidTimeRemotely']
        for location in location_entries['places']:
            JobLocation.objects.create(
                job=job_instance,
                is_remote=is_remote,
                is_covid_remote=is_covid_remote,
                city=location.get('city', ''),
                street=location.get('street', ''),
            )

    @staticmethod
    def _add_salary(salary_data: dict[str, str]) -> JobSalary:
        return JobSalary.objects.create(
            amount_from=salary_data['from'],
            amount_to=salary_data['to'],
            job_type=salary_data['type'],
            currency=salary_data['currency'],
        )


class JustJoinItDownloader(BaseDownloader):
    jobs_url = 'https://justjoin.it/api/offers'
    companies_url = 'https://justjoin.it/api/offers'

    @cached_property
    def job_board(self) -> JobBoard:
        return JobBoard.objects.get(name='justjoin.it')

    def download_companies(self) -> None:
        """
        There is no need to download companies.

        The companies data is downloaded from the same API that the jobs.
        """

    def download_jobs(self) -> None:
        response = requests.get(self.jobs_url)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            logger.error('Whoops, couldnt get offers from JustJoin.')
            return
        jobs = response.json()
        for job in tqdm(jobs):
            if Job.objects.filter(original_id=job['id']).exists():
                continue
            self._add_job(job)

    def _add_job(self, job: ResponseWithList) -> None:
        if all(job_type['salary'] is None for job_type in job['employment_types']):
            # we do not add jobs without salary
            return
        category, _ = JobCategory.objects.get_or_create(name=job['marker_icon'])
        salary = self._add_salary(job['employment_types'])
        company = self._add_or_update_company(job)
        technology, _ = Technology.objects.get_or_create(
            name=job['marker_icon'],
        )
        job_instance = Job.objects.create(
            original_id=job['id'],
            board=self.job_board,
            category=category,
            technology=technology,
            salary=salary,
            company=company,
            seniority=job['experience_level'].lower(),
            title=job['title'],
            url=f'https://justjoin.it/offers/{job["id"]}',
        )
        self._add_locations(job_instance, job)

    def _add_or_update_company(self, job: ResponseWithList) -> Company:
        possible_companies = Company.objects.get_possible_match(job['company_name'])
        size = self._parse_company_size(job['company_size'])
        if possible_companies.count() == 1:
            # if we have only one possible match, let's update if
            return possible_companies.first().update_if_better(
                url=job['company_url'],
                **size,
            )
        # if 0 or more than 1 possible matches, we create a new company
        # if there's more than 1, we can't be sure that this is the same one,
        # so we create a new company
        return Company.objects.create(
            name=job['company_name'],
            url=job['company_url'],
            **size,
        )

    @staticmethod
    def _add_salary(salary_data: list[dict[str, ResponseDictKeys]]) -> JobSalary:
        b2b_salary = [
            salary
            for salary in salary_data
            if salary['type'] == 'b2b'
        ]
        salary = b2b_salary[0] if b2b_salary else salary_data[0]
        return JobSalary.objects.create(
            amount_from=salary['salary']['from'],
            amount_to=salary['salary']['to'],
            job_type=salary['type'],
            currency=salary['salary']['currency'],
        )

    @staticmethod
    def _add_locations(job_instance: Job, job_raw_data: ResponseDictKeys) -> None:
        is_remote = job_raw_data['workplace_type'] == 'remote'
        is_covid_remote = job_raw_data['remote_interview']
        field_size = 32
        JobLocation.objects.create(
            job=job_instance,
            is_remote=is_remote,
            is_covid_remote=is_covid_remote,
            city=job_raw_data['city'][:field_size],
            street=job_raw_data['street'][:field_size],
        )
