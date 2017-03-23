import registration
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.http import require_GET, require_POST
import Queue

from marvglo.models import Employee, SaleItem, Transaction
from marvglo_crm.settings import MAX_EMPLOYEE_LEVEL, PERSONAL_BONUS_COMMISSION, VOLUME_BONUS_COMMISSION, RANK_TITLE_MAPPING


@require_GET
def index(request):
    global employee
    if not request.user.is_authenticated:
        ctx = {
            'isAuthenticated': request.user.is_authenticated,
        }
        return render(request, 'marvglo/home.html', ctx)

    # Collect transactions for lower levels
    if request.user.is_superuser:
        try:
            employee_id = request.GET['employee']
            try:
                employee = Employee.objects.filter(user=User.objects.get(username=employee_id)).get()
            except User.DoesNotExist or Employee.DoesNotExist:
                return render(request, 'marvglo/error.html', {'isAuthenticated': request.user.is_authenticated})
        except MultiValueDictKeyError:
            ctx = {
                'isAuthenticated': request.user.is_authenticated,
                'isAdmin': request.user.is_superuser and request.user.is_staff,
                'teamLeaders': list(Employee.objects.filter(level=0)),
                'title': 'admin'
            }
            return render(request, 'marvglo/home.html', ctx)
    else:
        employee = request.user.employee

    transactions = []
    transactions.extend(list(employee.transaction_set.all()))
    subEmployeeQueue = Queue.PriorityQueue()
    for sub_emp in list(employee.employee_set.all()):
        subEmployeeQueue.put(sub_emp)
    while not subEmployeeQueue.empty():
        sub_employee = subEmployeeQueue.get()
        transactions.extend(list(sub_employee.transaction_set.all()))
        for sub_emp in list(sub_employee.employee_set.all()):
            subEmployeeQueue.put(sub_emp)

    # calculate commissions
    personal_bonuses = []
    volume_bonuses = []
    for transaction_id in range(len(transactions)):
        for level in range(MAX_EMPLOYEE_LEVEL):
            personal_bonuses.append(
                round(
                    PERSONAL_BONUS_COMMISSION[level] * transactions[transaction_id].quantity * transactions[
                        transaction_id].sold_at_price, 2))
            volume_bonuses.append(
                round(
                    transactions[transaction_id].quantity * transactions[transaction_id].sold_at_price *
                    VOLUME_BONUS_COMMISSION[level][transactions[transaction_id].owner.level], 2))

        transactions[transaction_id].personal_bonus = personal_bonuses
        transactions[transaction_id].volume_bonus = volume_bonuses
        personal_bonuses = []
        volume_bonuses = []

    ctx = {
        'employee': employee,
        'isAuthenticated': request.user.is_authenticated,
        'adminApproved': employee.admin_approved,
        'isCashier': employee.is_cashier,
        'list_of_employees': list(Employee.objects.all()),
        'isAdmin': request.user.is_superuser and request.user.is_staff,
        'title': RANK_TITLE_MAPPING[employee.level],
        'transactions': transactions,
        'teamLeaders': list(Employee.objects.filter(level=0)),
        'items': list(SaleItem.objects.all())
    }
    return render(request, 'marvglo/home.html', ctx)


@receiver(registration.signals.user_registered)
def register_new_player(sender, **kwargs):
    employee = Employee(user=kwargs['user'])
    employee.save()


@login_required(login_url='reg/login/')
@require_GET
def remove_transaction(request, transaction_id):
    try:
        t = Transaction.objects.get(id=transaction_id)
        # check if user is cashier (have rights to view and change transactions)
        if request.user.employee.is_cashier:
            t.delete()
    except Transaction.DoesNotExist:
        # did not even exist
        pass
    return redirect(index)


@login_required(login_url='reg/login/')
@require_GET
def view_transaction(request, transaction_id):
    ctx = {
        'employee': request.user.employee,
        'isAuthenticated': request.user.is_authenticated,
        'adminApproved': request.user.employee.admin_approved,
        'items': list(SaleItem.objects.all())
    }
    try:
        t = Transaction.objects.get(id=transaction_id)
        # check if user is cashier (have rights to view and change transactions)
        if not request.user.employee.is_cashier:
            return redirect(index)
        ctx['transaction'] = t
    except Transaction.DoesNotExist:
        # did not even exist
        return render(request, 'marvglo/error.html', {'isAuthenticated': request.user.is_authenticated})
    return render(request, 'marvglo/transaction.html', ctx)


@require_POST
def submit_transaction(request):
    # TODO: Dict no entry error here. (although doesnt really matter as its a post)

    employee_id = Employee.objects.get(user=User.objects.get(username=request.POST['employeeId']))
    quantity = int(request.POST['quantity'])
    item = SaleItem.objects.get(name=request.POST['itemName'])
    # check there is enough product in stock
    if quantity <= item.stock:
        t = Transaction(item=item,
                        quantity=quantity,
                        submitted_by=request.user,
                        owner=employee_id,
                        sold_at_price=SaleItem.objects.get(name=request.POST['itemName']).price)
        t.save()
        item.stock -= quantity
        item.save()
    else:
        # TODO; redirect with error message
        pass
    return redirect(index)


@require_POST
def amend_transaction(request, transaction_id):
    try:
        t = Transaction.objects.get(id=transaction_id)
        # check if user is cashier (have rights to view and change transactions)
        if request.user.employee.is_cashier:
            item = SaleItem.objects.get(name=request.POST['itemName'])
            quantity = request.POST['quantity']
            # check that there is enough product in stock
            if quantity <= (t.quantity + item.stock):
                t.item = item
                t.quantity = quantity
                t.save()
    except Transaction.DoesNotExist:
        # did not even exist
        return render(request, 'marvglo/error.html', {'isAuthenticated': request.user.is_authenticated})
    return redirect(index)


@login_required(login_url='reg/login/')
def manage(request):
    if request.method == 'GET':
        employees = Employee.objects.filter(admin_approved=False)
        ctx = {
            'employee': request.user.employee,
            'isAuthenticated': request.user.is_authenticated,
            'any_unassigned': len(list(employees)) != 0,
            'unassigned_employees': list(employees),
            'title': RANK_TITLE_MAPPING[request.user.employee.level],
            'managers': list(Employee.objects.filter(level__lte=2))  # those who can manage lowest level employees
        }
        return render(request, 'marvglo/manage.html', ctx)
    else:
        try:
            employee = Employee.objects.get(user=User.objects.get(username=request.POST['employee']))
            manager = Employee.objects.get(user=User.objects.get(username=request.POST['manager']))
            employee.boss = manager
            employee.admin_approved = True
            employee.save()
        except:
            return render(request, 'marvglo/error.html', {'isAuthenticated': request.user.is_authenticated})
        return redirect(manage)


@login_required(login_url='reg/login/')
def create_user(request):
    if request.user.employee.is_cashier:
        if request.method == 'GET':
            ctx = {
                'isAuthenticated': request.user.is_authenticated,
                'title': RANK_TITLE_MAPPING[request.user.employee.level],
            }
            return render(request, 'marvglo/create_user.html', ctx)
        else:
            # create new django user
            user = User.objects.create_user(request.POST['email'], request.POST['email'], request.POST['password'])
            # create employee instance using django user
            Employee(user=user).save()
            return redirect(manage)
    else:
        return render(request, 'marvglo/error.html', {'isAuthenticated': request.user.is_authenticated})
