# manager views
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.views import generic

class IndexView(generic.TemplateView):
	template_name = "index.html"

def cluster_status(request):
	import cluster_status
	##cluster_status_context = get_cluster_status()
	##print cs.get_status()[0][0]
	return render_to_response("job_views/cluster_status.html", { "cluster_status": cluster_status.get_status() })

def view_simulations(request):
	import simulations
	return render_to_response("job_views/view_simulations.html", { "simulations": "blah" })

def create_simulation(request):
	return HttpResponse("Dummy Response")
