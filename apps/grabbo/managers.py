from django.db import models


class CompanyManager(models.Manager):
    def get_possible_duplicates(self, name):
        """There are different company names on different boards."""
        stripped_name = name.replace('sp. z o.o.', '')
        return self.filter(name__icontains=stripped_name)
