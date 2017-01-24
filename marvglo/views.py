import registration
from django.dispatch import receiver
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from marvglo.models import Employee


@require_GET
def index(request):
    ctx = {
        'isAuthenticated': request.user.is_authenticated,
    }
    return render(request, 'marvglo/home.html', ctx)


@receiver(registration.signals.user_registered)
def register_new_player(sender, **kwargs):
    employee = Employee(user=kwargs['user'])
    employee.save()


@require_GET
def remove_transaction(request, transaction_id):
    pass


@require_GET
def view_transaction(request, transaction_id):
    pass


@require_POST
def submit_transaction(request):
    pass


@require_POST
def amend_transaction(request, transaction_id):
    pass
