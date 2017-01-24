from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def index(request):
    ctx = {
        'isAuthenticated': request.user.is_authenticated,
    }
    return render(request, 'marvglo/home.html', ctx)


def remove_transaction(request, transaction_id):
    pass


def view_transaction(request, transaction_id):
    pass


def submit_transaction(request):
    pass


def amend_transaction(request, transaction_id):
    pass
