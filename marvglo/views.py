import registration
from django.dispatch import receiver
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST
import Queue

from marvglo.models import Employee, SaleItem, Transaction


@require_GET
def index(request):
    # Collect transactions for lower levels
    employee = request.user.employee
    transactions = []
    transactions.extend(list(employee.transaction_set.all()))
    subEmployeeQueue = Queue.PriorityQueue()
    for sub_emp in list(employee.employee_set.all()):
        subEmployeeQueue.put(sub_emp)
    # subEmployeeQueue.put(list(employee.employee_set.all()))
    while not subEmployeeQueue.empty():
        sub_employee = subEmployeeQueue.get()
        transactions.extend(list(sub_employee.transaction_set.all()))
        # subEmployeeQueue.put(list(sub_employee.employee_set.all()))
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
    try:
        t = Transaction.objects.get(id=transaction_id)
        # check transaction ownership
        if t.owner == request.user.employee:
            t.delete()
    except Transaction.DoesNotExist:
        # did not even exist
        pass
    return redirect(index)


@require_GET
def view_transaction(request, transaction_id):
    ctx = {
        'isAuthenticated': request.user.is_authenticated,
        'adminApproved': request.user.employee.admin_approved,
        'items': list(SaleItem.objects.all())
    }
    try:
        t = Transaction.objects.get(id=transaction_id)
        # check transaction ownership
        if t.owner != request.user.employee:
            return redirect(index)
        ctx['transaction'] = t
    except Transaction.DoesNotExist:
        # did not even exist
        return redirect(index)
    return render(request, 'marvglo/transaction.html', ctx)


@require_POST
def submit_transaction(request):
    t = Transaction(item=SaleItem.objects.get(name=request.POST['itemName']),
                    quantity=request.POST['quantity'],
                    owner=request.user.employee)
    t.save()
    return redirect(index)


@require_POST
def amend_transaction(request, transaction_id):
    try:
        t = Transaction.objects.get(id=transaction_id)
        # check transaction ownership
        if t.owner == request.user.employee:
            t.item = SaleItem.objects.get(name=request.POST['itemName'])
            t.quantity = request.POST['quantity']
            t.save()
    except Transaction.DoesNotExist:
        # did not even exist
        pass
    return redirect(index)
