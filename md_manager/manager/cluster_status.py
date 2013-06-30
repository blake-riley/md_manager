from manager.models import ClusterHost
import subprocess
import xml.etree.ElementTree as ET



## Returns job information and cluster status.
## TODO: Need to fix up catagorisation of running/idle/blocked jobs.
##	Correctly identify cores in use - current method is only a crude estimation
def get_status():

	host_list = []

	for host in ClusterHost.objects.all():

		## Will one day need to handle multiple communication pipelines.
		## In the event it is locally hosted on a cluster, should just call qstat directly

		qstat_command = "ssh %s@%s %s -x" % (host.username, host.hostname, host.qstat_cmd)
		qstat_xml = subprocess.check_output(qstat_command, shell=True)

		## Parse qstat xml output
		root = ET.fromstring(qstat_xml)
		job_list = []
		for child in root:
			job_dict = {}

			job_id = child.find("Job_Id").text.split(".")[0]
			job_name = child.find("Job_Name").text
			job_owner = child.find("Job_Owner").text.split("@")[0]
			try:
				nodes = child.find("Resource_List").find("nodes").text
				n_nodes = int(nodes.split(':')[0])
			except:
				n_nodes = 1
			try:
				ppn = int(nodes.split(':')[1].split('=')[1])
				cores = n_nodes*ppn
			except:
				cores = n_nodes
			try:
				work_dir = child.find("init_work_dir").text
			except:
				work_dir = ""

			job_dict['job_id'] = job_id
			job_dict['job_name'] = job_name
			job_dict['job_owner'] = job_owner
			job_dict['nodes'] = nodes
			job_dict['n_nodes'] = n_nodes
			job_dict['ppn'] = ppn
			job_dict['cores'] = cores
			job_dict['work_dir'] = work_dir

			job_list.append(job_dict)

		n_jobs = len(root)


		pbsnodes_command = "ssh %s@%s pbsnodes -x" % (host.username, host.hostname)
		pbsnodes_xml = subprocess.check_output(pbsnodes_command, shell=True)

		## Parse pbsnodes output and compute cluster availability.

		total_procs = 0
		active_procs = 0

		nodes_root = ET.fromstring(pbsnodes_xml)
		for node in nodes_root:
			np = node.find("np").text
			state = node.find("state").text
			if state != "down" and state != "offline":
				total_procs = total_procs + int(np)
			if state == "job-exclusive":
				active_procs = active_procs + int(np)

		percentage_active = round(float(active_procs)/float(total_procs)*100, 2)

		status = [n_jobs, active_procs, total_procs, percentage_active]

		# for line in showq.split('\n'):
		# 	if line.find("Processors Active") > 0:
		# 		active_procs = line.lstrip().rstrip()

		host_list.append((host, status, job_list))

	return host_list