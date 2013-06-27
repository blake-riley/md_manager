import subprocess
import xml.etree.ElementTree as ET
import sqlite3

import settings

def get_jobs():

	command = "ssh %s@%s qstat -x" % (settings.user, settings.host)

	qstat_xml = subprocess.check_output(command, shell=True)

	root = ET.fromstring(qstat_xml)

	job_list = []

	for child in root:
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
		job_list.append((job_id, job_name, job_owner, cores, work_dir))


	return_html = """<table class='table table-striped'><thead>
		<tr><td><b>Job Id</b></td><td><b>Job Name</b></td><td><b>Job Owner</b></td><td><b>Cores</b></td></tr></thead>"""

	for job in job_list:
		job_row = """<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>""" % (job[0], job[1], job[2], job[3])
		return_html = return_html + job_row

	return_html = return_html + """</table>"""

	return return_html




def get_sims():


	return_html = """<table class='table table-striped'><thead>
		<tr><td><b>Job Id</b></td><td><b>Job Name</b></td><td><b>Job Owner</b></td><td><b>Cores</b></td></tr></thead>"""


	return_html = return_html + """</table>"""

	return return_html


