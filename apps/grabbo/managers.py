from django.db import models


class CompanyManager(models.Manager):
    def get_possible_match(self, name: str) -> models.QuerySet:
        """There are different company names on different boards."""
        # TODO: matching by company url
        stripped_name = name.replace('sp. z o.o.', '').strip()
        # if name didn't have sp. z o.o., let's add it to the check
        name_with_sp = f'{stripped_name} sp. z o.o.'
        return (
            self.filter(name__iexact=stripped_name)
            | self.filter(name__iexact=name_with_sp)
        )
