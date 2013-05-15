# Create your views here.

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse


# --------- url mapping method -----------------------------------------


def home(request):
    return HttpResponse('<h1>Welcome come to logtoeye!</h1>')


def dashboard(request, template="dashboard.html"):
    """
    datagrid show
    """
    context = {}
    return render(request, template, context)


def builder(request, template="uibuilder.html"):
    """
    homepage...
    """
    context = {}
    return render(request, template, context)