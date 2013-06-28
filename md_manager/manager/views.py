# manager views
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.views import generic

class IndexView(generic.TemplateView):
	template_name = "index.html"

def active_jobs(request):
	return render_to_response("job_views/active_jobs.html", { "blah": "test var" })

def active_simulations(request):
	return HttpResponse("Dummy Response")

def create_simulation(request):
	return HttpResponse("Dummy Response")
