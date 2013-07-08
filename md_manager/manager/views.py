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
	from manager.models import Simulation
	from manager.models import Project
	return render_to_response("job_views/view_simulations.html", { "projects": Project.objects.all(),
																	"simulations": Simulation.objects.all() })
def update_simulations(request):
	from django.http import HttpResponseRedirect
	import simulations
	## Perform the update here
	if "p" in request.GET:
		## Update project
		simulations.update_status(request.GET["p"])
	else:
		## Update all simulations
		simulations.update_status_all()

	## Redirect to view_simulations page
	return HttpResponseRedirect("/view_simulations")





def create_simulation(request):
	return render_to_response("simulations/create_new.html")
