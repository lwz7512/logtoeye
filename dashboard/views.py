# Create your views here.

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse

import models
import reportor

# --------- url mapping method -----------------------------------------


def home(request):
    return HttpResponse("<h1>Welcome come to logtoeye!</h1>"
                        "<a href='/dashboard'>Click here to Get Started</a>")


def dashboard(request, template="dashboard.html"):
    """
    datagrid show
    """
    context = {}
    return render(request, template, context)


def report(request, template="report.html"):
    """
    daily report
    """
    context = {}
    return render(request, template, context)


def config(request, template="config.html"):
    """
    app config
    """
    context = {}
    return render(request, template, context)


def builder(request, template="uibuilder.html"):
    """
    homepage...
    """
    context = {}
    return render(request, template, context)


def preview_report(request, template="report_preview.html"):
    """
    homepage...
    """
    context = {}
    # return render(request, template, context)
    html = reportor.create()
    return HttpResponse(html)