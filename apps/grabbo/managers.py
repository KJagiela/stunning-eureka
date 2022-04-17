from django.db import models


class CompanyManager(models.Manager):
    def get_possible_match(self, name):
        """There are different company names on different boards."""
        # TODO: matching by company url
        stripped_name = name.replace('sp. z o.o.', '').strip()
        return self.filter(name__iexact=stripped_name)
