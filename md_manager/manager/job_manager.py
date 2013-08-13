import subprocess
import time

class Host:
	
	"""A general definition of a server.

	Contains general functions which should work for servers of all queue-managers.

	Can ONLY be used as a parent class for queue-manager server classes.

	Required variables:
	 - username
	 - hostname

	Provided procedures:
	 - get_status()
	 - update_status()
	 - update_time()

	Provided classes:
	 - CommandList
	 - Job
	"""
	def __init__(self, username, hostname):
		self.username = username
		self.hostname = hostname

		self.cluster_status = dict()
		self.job_list = dict()

	class CommandList:
		pass

	class Job(dict):
	    def __init__(self, **kwargs):
	        dict.__init__(self, **kwargs)
	        self.__dict__ = self

	def get_status(self):
		return self.cluster_status, self.job_list

	def update_status(self):
		try:
			self.update_job_status()
			self.update_cluster_status()
		except:
			#	TODO: pass this exception up to Django interface
			raise
		else:
			return self.get_status()



class SlurmHost(Host):
	
	"""A definition of a server which uses the SLURM queue manager.

	Provided procedures:
	 - update_job_status()
	 - parse_jobstring()

	"""

	def __init__(self, username, hostname):
		
		#	Initialise as a subclass of Host
		Host.__init__(self, username, hostname)

		#	Fill in default queue-manager specific commands
		self.cmds = self.CommandList()
		self.cmds.flags = {
			'user': '-u {0} '
		}
		self.cmds.ssh = "ssh {0}@{1} {2}".format(self.username, self.hostname, '{0}')
		# self.cmds.get_jobs = "\"squeue -u {0} -o \'%i %j %B %a %u %U %g %G %D %C %T %S %e %l %M %L %k %s\' -h {1} \" ".format(self.username, '{0}')
		# self.cmds.get_jobids = "\"squeue -o \'%i\' -h {0} {1} \" "
		self.cmds.get_jobdetails = "scontrol -d -o show job {0} "
		self.cmds.get_clusterstatus = "\"sinfo -o \'%C %F\' -h\" "

		#	May consider calling self.update_status() from here.

	def update_job_status(self, jobid=None):

		#	Develop the command to be ssh'd ---
		#		if jobid is empty, then update all jobs
		#		if jobid has a single value, we are updating the specified jobid.
		if jobid == None:
			command = self.cmds.get_jobdetails.format('')
		else:
			assert jobid.isdigit()
			command = self.cmds.get_jobdetails.format(jobid)

		#	Now, run the ssh command to get the information
		rawstatus = subprocess.check_output(self.cmds.ssh.format(command), shell=True)

		#	If python<2.7, may need to instead:
		#proc = subprocess.Popen(<command>, shell=True, stdout=subprocess.PIPE)
		#rawstatus = proc.stdout.read()

		#	Split into a list, remove empty lines.
		entrylist = rawstatus.split('\n')
		entrylist = filter(None, entrylist)

		#	If updating all jobs, declare all jobs to be 'DEAD'.
		#	This will be removed if updated, otherwise, job is no longer running on server.
		#	Dead jobs can be pruned from the job list later.
		if jobid == None:
			for jobid, job in self.job_list.iteritems():
				job['jobstate'] = 'DEAD' 

		#	Now, parse!
		for line in entrylist:
			parsedjob_id, parsedjob = self.parse_jobdetailstring(line)

			#	If parsedjob_id is not already in the job_list, add it.
			#	If it is, and it is newer than the pre-existing entry, update it.
			#	Else, do nothing.
			if parsedjob_id not in self.job_list.keys():
				self.job_list[parsedjob_id] = parsedjob
			else:
				existingjob = self.job_list[parsedjob_id]
				if parsedjob['last_updated'] > existingjob['last_updated']:
					self.job_list[parsedjob_id] = parsedjob
				else:
					#	The parsedjob information is not newer than the existingjob info.
					pass


	def parse_jobdetailstring(self, jobstring):
		"""Takes a one line, one job output of scontrol, 
		and creates a job instance from it.
		"""

		#	Create new job instance
		parsedjob = self.Job()

		#	Add a new dictionary entry for each job attribute
		for item in jobstring.split():
			iparted = item.partition('=')
			parsedjob[iparted[0].lower()] = iparted[2]

		#	Add update time to the parsedjob
		parsedjob['last_updated'] = time.time()

		return parsedjob['jobid'], parsedjob


	def update_cluster_status(self):

		#	First, run the ssh command to get the information
		rawstatus = subprocess.check_output(self.cmds.ssh.format(self.cmds.get_clusterstatus), shell=True)
		#	TODO: DEBUGONLY raw_cluster_status should not be an embedded variable.
		self.raw_cluster_status = rawstatus

		statuslist = rawstatus.split('\n')[0].split()

		#	Now, parse!
		try:
			self.cluster_status['procs'] = self.parse_statusstring(statuslist[0])
			self.cluster_status['nodes'] = self.parse_statusstring(statuslist[1])
		except:
			raise
		else:
			self.cluster_status['last_updated'] = time.time()


	def parse_statusstring(self, statusstring):
		entry = statusstring.split('/')

		statusdict = dict(
			alloc = self.parse_number(entry[0]),
			idle = self.parse_number(entry[1]),
			other = self.parse_number(entry[2]),
			total = self.parse_number(entry[3])
			)
		
		return statusdict

	def parse_number(self, nstr):
		if not nstr.isdigit():
			nstr_l = int(nstr[:-1])
			nstr_r = nstr[-1:]
			if nstr_r == 'K':
				nstr_r = 2 ** 10
			elif nstr_r == 'M':
				nstr_r = 2 ** 20
			elif nstr_r == 'G':
				nstr_r = 2 ** 30
			else:
				raise Exception
			nstr = nstr_l * nstr_r

		return int(nstr)



#	TESTING:
Avoca = SlurmHost('briley', 'avoca.vlsci.unimelb.edu.au')

Avoca.get_status()
Avoca.update_status()


def get_userjobs(host, username):
	filter_job_list = {}
	
	for jobid, job in host.job_list.iteritems():
		if username in job['userid']:
			filter_job_list[jobid] = job 

	return filter_job_list

get_userjobs(Avoca, 'briley')



#	TODO:
#	-	Change behaviour so that if run locally on a cluster, can run commands without ssh.

