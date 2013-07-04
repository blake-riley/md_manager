from manager.models import ClusterHost
from manager.models import Simulation
import subprocess

import hpc


def get_simulations():
	job_list = get_job_list()
	for sim in Simulation.objects.all():
		check_simulation_for_job(sim, job_list)


def check_simulation_for_job(simulation, job_list):

	simulation.active = False

	for host in job_list:
		if simulation.assigned_cluster == host[0]:
			for job in host[1]:
				if job["job_name"].find(simulation.suffix) >0:
					simulation.active = True

	## Check simulation for completion
	if simulation.active == False and simulation.complete == False and simulation.failed == False:
		print "checking simulation on assigned cluster"
		check_gromacs_job(simulation)


	simulation.save()


def check_gromacs_job(simulation):
	print "Checking gromacs simulation"

	host = hpc.HPC(simulation.assigned_cluster.username, simulation.assigned_cluster.hostname)

	log_files, err = host.get_OutputError("ls -1 %s/*.logout" % (simulation.work_dir))

	past_log = ""
	past_log_index = 0
	for index, log_file in enumerate(log_files.split('\n')):
		if log_file == "":
			continue
		

		#print "Checking log file: %s" % (log_file)
		tail, err = host.get_OutputError("tail %s" % (log_file))
		if tail.find("Performance") < 0:
			print "Simulation stopped at: %s" % (past_log)
			break

		past_log = log_file
		past_log_index = index

	print past_log_index
	print len(log_files.split('\n'))
	if past_log_index < len(log_files.split('\n')):
		simulation.active = False
		simulation.failed = True
		print "Simulation has crashed."
	else:
		simulation.active = False
		simulation.failed = False
		simulation.complete = True









def check_namd_job(simulation):
	print "Checking NAMD simulation"



def get_job_list():
	import cluster_status

	host_list = []

	for host in ClusterHost.objects.all():
		job_list = cluster_status.parse_qstat(host.username, host.hostname, host.qstat_cmd)
		host_list.append((host, job_list))

	return host_list