from django.db import models


class HypeStatus(models.IntegerChoices):
    UNKNOWN = 0  # special case
    FUCK_IT = 1
    INTERESTED = 2
    HYPED = 3
