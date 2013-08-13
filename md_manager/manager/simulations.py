from manager.models import ClusterHost
from manager.models import Simulation
from manager.models import Project
import subprocess
import pytz
import hpc


def update_status(project_id):
	job_list = get_job_list()

	project = Project.objects.get(id=project_id)

	for sim in project.simulation_set.all():
		sim.state = ""
		sim.simulation_rate = None
		check_simulation_for_job(sim, job_list)


def update_status_all():
	job_list = get_job_list()
	for sim in Simulation.objects.all():
		check_simulation_for_job(sim, job_list)


def check_simulation_for_job(simulation, job_list):
	from datetime import datetime, timedelta

	## local timezone of machine to stop django whinging
	machine_timezone = pytz.timezone("Australia/Melbourne")

	if simulation.state != "Complete":
		simulation.state = ""	## Reset state
	simulation.notes = ""	## Reset notes
	for host in job_list:
		if simulation.assigned_cluster == host[0]:
			for job in host[1]:
				if job["job_name"].find(simulation.job_uuid) != -1:
					simulation.last_known_jobid = job["job_id"]
					simulation.n_cores = job["cores"]
					try:
						progression = (int(job["job_name"].split("MD")[1]) - 1) * int(simulation.project.production_protocol.ns_per_block)
						simulation.progression = str(progression)
					except:
						simulation.progression = None

					if job["state"] == "R":
						simulation.state = "Active"
					if job["state"] == "Q":
						simulation.state = "Idle"
					if job["state"] == "H":
						simulation.state = "Idle"

	## Check simulation for completion
	if simulation.state == "" or simulation.simulation_rate == None:
		print "Checking simulation on assigned cluster"
		if simulation.project.simulation_package.name == "gromacs":
			check_gromacs_job(simulation)
		elif simulation.project.simulation_package.name == "namd":
			check_namd_job(simulation)


	if simulation.progression != None and simulation.simulation_rate != 0 and simulation.simulation_rate != None:
		estimated_completion = float(simulation.project.production_protocol.total_ns - float(simulation.progression))/float(simulation.simulation_rate)
		simulation.estimated_completion = datetime.now() + timedelta(days=estimated_completion)

		## fix timezone
		simulation.estimated_completion = simulation.estimated_completion.replace(tzinfo=machine_timezone)

	simulation.save()


## Checks the rate and 
def check_gromacs_job(simulation):
	print "Checking gromacs job for simulation rate and failure or completion"

	host = hpc.HPC(simulation.assigned_cluster.username, simulation.assigned_cluster.hostname)
	performance, err = host.get_OutputError("tail %s/*.logout | grep 'Performance'" % (simulation.work_dir))

	if err:
		#Error, directory doesn't exist.
		simulation.notes = "Error: Cannot locate simulation working directory!"
	else:
		rate_lines = performance.split('\n')
		rate_counter = 0
		last_rate = None
		for line in rate_lines:
			if line.strip() != "":
				last_rate = line
				rate_counter += 1

		if simulation.state != "Active":
			if rate_counter < simulation.project.production_protocol.n_blocks:
				simulation.state = "Fail"
				simulation.notes = "Error: Failed at %d" % rate_counter
			else:
				simulation.state = "Complete"
				simulation.progression = None

		try:
			simulation.simulation_rate = round(float(last_rate.split()[3]), 3) ## ns/day
		except:
			simulation.simulation_rate = None


def check_namd_job(simulation):
	print "Checking NAMD simulation"

	host = hpc.HPC(simulation.assigned_cluster.username, simulation.assigned_cluster.hostname)
	performance, err = host.get_OutputError("tail %s/*.log | grep 'WallClock'" % (simulation.work_dir))

	if err:
		#Error, directory doesn't exist.
		simulation.notes = "Error: Cannot locate simulation working directory!"
	else:
		rate_lines = performance.split('\n')
		rate_counter = 0
		last_rate = None
		for line in rate_lines:
			if line.strip() != "":
				last_rate = line
				rate_counter += 1

		if simulation.state != "Active":
			if len(rate_lines) - 1 < simulation.project.production_protocol.n_blocks:
				simulation.state = "Fail"
				simulation.notes = "Error: Failed at %d" % (rate_counter+1)
			else:
				simulation.state = "Complete"

		try:
			rate_ns_day = round(1/(float(last_rate.split()[1])/simulation.project.production_protocol.ns_per_block/60/60/24), 3)
		except:
			rate_ns_day = None


		simulation.simulation_rate = rate_ns_day ## ns/day

def get_job_list():
	import cluster_status

	host_list = []
	for host in ClusterHost.objects.all():
		job_list = cluster_status.parse_qstat(host.username, host.hostname, host.qstat_cmd)
		host_list.append((host, job_list))
	return host_list