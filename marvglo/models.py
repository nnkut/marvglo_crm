from __future__ import unicode_literals
from django.contrib.auth.models import User

from django.db import models


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # level higher guy
    boss = models.ForeignKey("self", on_delete=models.DO_NOTHING, blank=True, null=True)
    level = models.IntegerField(default=1)
    admin_approved = models.BooleanField(default=False)

    def __str__(self):
        return '[' + str(self.level) + '] ' + self.user.username


class SaleItem(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField(default=0.0)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    # TODO: fill this model fully
    item = models.ForeignKey(SaleItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    # sold by
    owner = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return '[' + str(self.item.id) + '] : ' + str(self.item) + ' : ' + str(self.quantity) + 'pcs'
