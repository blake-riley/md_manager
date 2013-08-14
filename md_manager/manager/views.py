# manager views
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.views import generic

class IndexView(generic.TemplateView):
	template_name = "index.html"

def cluster_status(request):
	import cluster_status
	from manager.models import ClusterHost
	from manager.models import ClusterJob

	## Update ClusterJobs for all ClusterHosts
	## Eventually move this to a button...
	for host in ClusterHost.objects.all():
		host.update_queue()

	return render_to_response("job_views/cluster_status.html", { "clusterjobs": ClusterJob.objects.all(),
																	"clusterhosts": ClusterHost.objects.all() })



def view_simulations(request):
	from manager.models import Simulation
	from manager.models import Project
	return render_to_response("job_views/view_simulations.html", { "projects": Project.objects.all(),
																	"simulations": Simulation.objects.all() })
def update_simulations(request, project_id = None):
	from django.http import HttpResponseRedirect
	from manager.models import Project
	from manager.models import Simulation
	from manager.models import ClusterHost

	## Update all clusters first
	for host in ClusterHost.objects.all():
		host.update_queue()

	## Perform the update here
	if project_id == None:
		## Update all simulations
		for project in Project.objects.all():
			for sim in project.simulation_set.all():
				sim.update_simulation()
	else:
		for sim in Project.objects.get(id=project_id).simulation_set.all():
		## Update specific project
			sim.update_simulation()

	## Redirect to view_simulations page
	return HttpResponseRedirect("/view_simulations")





def view_analysis(request, project_id):
	from manager.models import Project

	return render_to_response("analysis_views/view_analysis.html", { "project": Project.objects.get(id=project_id) })




def create_simulation(request):
	return render_to_response("simulations/create_new.html")
