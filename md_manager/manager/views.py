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
def update_simulations(request, sim_id = None):
	from django.http import HttpResponseRedirect
	import simulations
	## Perform the update here
	if sim_id == None:
		## Update all simulations
		simulations.update_status_all()
	else:
		## Update project
		simulations.update_status(int(sim_id))
	## Redirect to view_simulations page
	return HttpResponseRedirect("/view_simulations")


def view_analysis(request, sim_id):
	from manager.models import Project

	return render_to_response("analysis_views/view_analysis.html", { "project": Project.objects.get(id=sim_id) })




def create_simulation(request):
	return render_to_response("simulations/create_new.html")
