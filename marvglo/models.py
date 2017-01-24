from __future__ import unicode_literals
from django.contrib.auth.models import User

from django.db import models


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)

    def __str__(self):
        return '[' + str(self.level) + '] ' + self.user.username


class Transaction(models.Model):
    # TODO: fill this model fully
    item_name = models.CharField(max_length=200)

    owner = models.ForeignKey(Employee, on_delete=models.CASCADE)
