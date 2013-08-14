'''
gromacs.py
Abstraction layer for setting up, checking on and performing analysis of gromacs simulations.
'''

from manager.models import ClusterJob
from datetime import datetime, timedelta
import pytz

machine_timezone = pytz.timezone("Australia/Melbourne")

def update_simulation(sim):
	print sim

	if sim.state != "Complete":
		sim.state = ""	## Reset simulation state
	sim.notes = "" ## Reset simulation notes

	## Check for a job that matches sim in ClusterJob
	for job in ClusterJob.objects.all():
		if job.job_name.find(sim.job_uuid) != -1:
			## If we are here - we have found a matching job.
			## Update info from job
			sim.state = job.state
			sim.last_known_jobid = job.job_id
			sim.n_cores = job.n_cores

			try:
				progression = (int(job.job_name.split("MD")[1]) - 1) * int(sim.project.production_protocol.ns_per_block)
				sim.progression = str(progression)
			except:
				sim.progression = None

			break


	## Check for simulation completion or failure.
	if sim.state == "" or sim.simulation_rate == None:
		performance, err = sim.assigned_cluster.exec_cmd("tail %s/*.logout | grep 'Performance'" % (sim.work_dir))

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

			if sim.state != "Active":
				if rate_counter < sim.project.production_protocol.n_blocks:
					sim.state = "Fail"
					sim.notes = "Error: Failed at %d" % rate_counter
				else:
					sim.state = "Complete"
					sim.progression = None

			try:
				sim.simulation_rate = round(float(last_rate.split()[3]), 3) ## ns/day
			except:
				sim.simulation_rate = None


	## Update sestimated completion date
	if sim.progression != None and sim.simulation_rate != 0 and sim.simulation_rate != None:
		estimated_completion = float(sim.project.production_protocol.total_ns - float(sim.progression))/float(sim.simulation_rate)
		sim.estimated_completion = datetime.now() + timedelta(days=estimated_completion)

		## fix timezone issue
		sim.estimated_completion = sim.estimated_completion.replace(tzinfo=machine_timezone)


	sim.save()

