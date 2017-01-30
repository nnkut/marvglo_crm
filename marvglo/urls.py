from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^transaction/remove/(?P<transaction_id>[0-9]+)/', views.remove_transaction),
    url(r'^transaction/(?P<transaction_id>[0-9]+)/', views.view_transaction),
    url(r'^transaction/submit', views.submit_transaction),
    url(r'^transaction/amend/(?P<transaction_id>[0-9]+)', views.amend_transaction),
    url(r'^manage/', views.manage),
    url(r'^$', views.index),
]