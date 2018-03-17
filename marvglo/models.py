from __future__ import unicode_literals
from django.contrib.auth.models import User

from django.db import models
from django.utils import timezone

from marvglo_crm.settings import RANK_TITLE_MAPPING


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # level higher guy
    boss = models.ForeignKey("self", on_delete=models.DO_NOTHING, blank=True, null=True)
    title = models.CharField(choices=map(lambda t: (t, t), RANK_TITLE_MAPPING), max_length=50, default='Supervisor')
    level = models.IntegerField(default=3)
    admin_approved = models.BooleanField(default=False)
    # determines whether user is able to input sales
    is_cashier = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        try:
            self.level = RANK_TITLE_MAPPING.index(self.title)
        except ValueError:
            # title is broken - use old level instead
            pass
        super(Employee, self).save(*args, **kwargs)


class SaleItem(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField(default=0.0)
    # number of items available
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    item = models.ForeignKey(SaleItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    sold_at_price = models.FloatField(default=0)
    # sold by employee
    owner = models.ForeignKey(Employee, on_delete=models.CASCADE)
    # cashier this was submitted by
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    date_time_created = models.DateTimeField(blank=True, null=True, default=timezone.now)

    discounted = models.BooleanField(default=False)

    # commissions (not stored in db, just a list computed when transactions are gathered)
    personal_bonus = []
    volume_bonus = []

    def __str__(self):
        return '[' + str(self.item.id) + '] : ' + str(self.item) + ' : ' + str(self.quantity) + 'pcs'
