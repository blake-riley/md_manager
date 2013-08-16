'''
namd.py
Abstraction layer for setting up, checking on and performing analysis of NAMD simulations.
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
		if job.job_name.find(sim.job_uuid) != -1 and job.state != "Complete":
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

######## NAMD specific code ##########
	if sim.state == "" or sim.simulation_rate == None:
		## Check for simulation completion or failure.
		performance, err = sim.assigned_cluster.exec_cmd("tail %s/*.log | grep 'WallClock'" % (sim.work_dir))

		if err:
			#Error, directory doesn't exist.
			sim.notes = "Error: Cannot locate simulation working directory!"
		else:
			rate_lines = performance.split('\n')
			rate_counter = 0
			last_rate = None
			for line in rate_lines:
				if line.strip() != "":
					last_rate = line
					rate_counter += 1

			if sim.state != "Active":
				if len(rate_lines) - 1 < sim.project.production_protocol.n_blocks:
					sim.state = "Fail"
					sim.notes = "Error: Failed at %d" % (rate_counter+1)
				else:
					sim.state = "Complete"

			try:
				rate_ns_day = round(1/(float(last_rate.split()[1])/sim.project.production_protocol.ns_per_block/60/60/24), 3)
			except:
				rate_ns_day = None


			sim.simulation_rate = rate_ns_day ## ns/day


########## End NAMD specific code ##########

	## Update sestimated completion date
	if sim.progression != None and sim.simulation_rate != 0 and sim.simulation_rate != None:
		estimated_completion = float(sim.project.production_protocol.total_ns - float(sim.progression))/float(sim.simulation_rate)
		sim.estimated_completion = datetime.now() + timedelta(days=estimated_completion)

		## fix timezone issue
		sim.estimated_completion = sim.estimated_completion.replace(tzinfo=machine_timezone)


	sim.save()





def request_trajectory(sim):
	print "Requesting namd trajectory."



