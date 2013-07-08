from manager.models import ClusterHost
from manager.models import Simulation
from manager.models import Project
import subprocess

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

	if simulation.state != "Complete":
		simulation.state = ""	## Reset state
	simulation.notes = ""	## Reset notes
	for host in job_list:
		if simulation.assigned_cluster == host[0]:
			for job in host[1]:
				if job["job_name"].find(simulation.job_uuid) != -1:
					simulation.last_known_jobid = job["job_id"]
					simulation.n_cores = job["cores"]
					progression = (int(job["job_name"].split("MD")[1]) - 1) * int(simulation.project.production_protocol.ns_per_block)
					simulation.progression = str(progression)

					if job["state"] == "R":
						simulation.state = "Active"
					if job["state"] == "Q":
						simulation.state = "Idle"
					if job["state"] == "H":
						simulation.state = "Idle"

	if simulation.simulation_rate == None:
		check_gromacs_simulation_rate(simulation)

	if simulation.progression != None:
		estimated_completion = float(simulation.project.production_protocol.total_ns - float(simulation.progression))/float(simulation.simulation_rate)
		simulation.estimated_completion = datetime.now() + timedelta(days=estimated_completion)

	## Check simulation for completion
	if simulation.state == "":
		print "Checking simulation on assigned cluster"
		# if simulation.project.software_package == ""
		check_gromacs_job(simulation)


	simulation.save()


def check_gromacs_simulation_rate(simulation):
	print "Checking gromacs job for simulation rate"

	host = hpc.HPC(simulation.assigned_cluster.username, simulation.assigned_cluster.hostname)
	performance, err = host.get_OutputError("grep 'Performance' %s/*.logout" % (simulation.work_dir))

	if err:
		#Error, directory doesn't exist.
		simulation.notes = "Error: Cannot locate simulation working directory!"
	else:
		rate_lines = performance.split('\n')
		last_rate = rate_lines[len(rate_lines)-2]

		simulation.simulation_rate = last_rate.split()[3] ## ns/day


def check_gromacs_job(simulation):
	print "Checking gromacs simulation"

	host = hpc.HPC(simulation.assigned_cluster.username, simulation.assigned_cluster.hostname)
	log_files, err = host.get_OutputError("ls -1 %s/*.logout" % (simulation.work_dir))

	cmd = ""
	for index, log_file in enumerate(log_files.split('\n')):
		if log_file == "":
			continue
		cmd += "tail %s; echo '||'; " % (log_file)

	tail, err = host.get_OutputError(cmd)
	log_index = 0
	for i, tail_log in enumerate(tail.split('||')):
		log_index = i
		if tail_log.find("Performance") < 0:
	 		break

	if (len(tail.split('||')) - 1) == 0:
		simulation.state = "Fail"
		simulation.notes = "Error: Unable to locate simulation work_directory."
	else:
		if log_index < (len(tail.split('||')) - 1):
			simulation.state = "Fail"
			simulation.notes = "Error: Failed at %d" % log_index
		else:
			simulation.state = "Complete"






def check_namd_job(simulation):
	print "Checking NAMD simulation"



def get_job_list():
	import cluster_status

	host_list = []
	for host in ClusterHost.objects.all():
		job_list = cluster_status.parse_qstat(host.username, host.hostname, host.qstat_cmd)
		host_list.append((host, job_list))
	return host_list