import registration
from django.dispatch import receiver
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
import Queue

from marvglo.models import Employee, SaleItem


@require_GET
def index(request):

    # Collect transactions for lower levels
    employee = request.user.employee
    transactions = []
    transactions.extend(list(employee.transaction_set.all()))
    subEmployeeQueue = Queue.PriorityQueue()
    for sub_emp in list(employee.employee_set.all()):
        subEmployeeQueue.put(sub_emp)
    #subEmployeeQueue.put(list(employee.employee_set.all()))
    while not subEmployeeQueue.empty():
        sub_employee = subEmployeeQueue.get()
        transactions.extend(list(sub_employee.transaction_set.all()))
        #subEmployeeQueue.put(list(sub_employee.employee_set.all()))
        for sub_emp in list(sub_employee.employee_set.all()):
            subEmployeeQueue.put(sub_emp)

    ctx = {
        'isAuthenticated': request.user.is_authenticated,
        'adminApproved': employee.admin_approved,
        'transactions': transactions,
        'items': list(SaleItem.objects.all())
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
