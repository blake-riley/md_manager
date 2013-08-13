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
		self.cmds.ssh = "ssh {0}@{1} {2}".format(self.username, self.hostname, '{0}')
		self.cmds.list_jobs = "\"squeue -u {0} -o \'%i %j %B %a %u %U %g %G %D %C %T %S %e %l %M %L %k %s\' -h {1} \" ".format(self.username, '{0}')
		self.cmds.list_clusterstatus = "\"sinfo -o \'%C %F\' -h\" "

		#	May consider calling self.update_status() from here.


	def update_job_status(self, jobid_list=[]):

		#	Develop the command to be ssh'd ---
		#		if jobid_list is empty, then we are updating all jobs
		#		if jobid_list has values, we are updating only the specified jobids.
		if len(jobid_list) == 0:
			command = self.cmds.list_jobs.format('')
		else:
			jobid_string = '--jobs='
			for jobid in jobid_list:
				jobid_string += str(jobid)+','
			jobid_string = jobid_string[:-1]	#	Remove the final comma
			command = self.cmds.list_jobs.format(jobid_string)

		#	Now, run the ssh command to get the information
		rawstatus = subprocess.check_output(self.cmds.ssh.format(command), shell=True)

		#	If python<2.7, may need to instead:
		#proc = subprocess.Popen(<command>, shell=True, stdout=subprocess.PIPE)
		#rawstatus = proc.stdout.read()

		#	Split into a list, remove empty lines.
		entrylist = rawstatus.split('\n')
		entrylist = filter(None, entrylist)

		#	Now, parse!
		for line in entrylist:
			parsedjob_id, parsedjob = self.parse_jobstring(line)

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


	def parse_jobstring(self, jobstring):
		entry = jobstring.split()

		parsedjob = self.Job(
			jobid = entry[0],
			last_updated = time.time(),
			jobname = entry[1],
			exec_host = entry[2],
			account = entry[3],
			username = entry[4],
			userid = entry[5],
			group = entry[6],
			groupid = entry[7],
			nodes = entry[8],
			cpus = entry[9],
			jobstate = entry[10],
			time_start = entry[11],
			time_end = entry[12],
			time_limit = entry[13],
			time_running = entry[14],
			time_remaining = entry[15],
			comment = entry[16],
			geometry = entry[20]
			)

		return parsedjob['jobid'], parsedjob

	def update_cluster_status(self):

		#	First, run the ssh command to get the information
		rawstatus = subprocess.check_output(self.cmds.ssh.format(self.cmds.list_clusterstatus), shell=True)
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


#	TODO:
#	-	Change behaviour so that if run locally on a cluster, can run commands without ssh.
#	-	Learn to parse the following command:
#		>	scontrol -o show job 456149
#		>>	JobId=456149 Name=GZMB.Mm.empty_run2.MD003 UserId=briley(3806) GroupId=VR0071(581) Priority=8396 Account=vr0071 QOS=normal JobState=RUNNING Reason=None Dependency=(null) Requeue=0 Restarts=0 BatchFlag=1 ExitCode=0:0 RunTime=3-17:09:16 TimeLimit=5-00:00:00 TimeMin=N/A SubmitTime=2013-08-08T01:17:20 EligibleTime=2013-08-08T01:17:20 StartTime=2013-08-08T01:17:20 EndTime=2013-08-13T01:17:21 PreemptTime=None SuspendTime=None SecsPreSuspend=0 Partition=main AllocNode:Sid=avoca-lb:29326 ReqMidplaneList=(null) ExcMidplaneList=(null) MidplaneList=bgq1011[30101x30231] BatchHost=avoca-lb NumNodes=8 NumCPUs=128 CPUs/Task=1 ReqS:C:T=*:*:* MinCPUsNode=1 MinMemoryNode=0 MinTmpDiskNode=0 Features=(null) Gres=(null) Reservation=(null) Shared=OK Contiguous=0 Licenses=(null) Network=(null) Command=/vlsci/VR0071/briley/GranzymeB/NAMD2/GZMB.Mm.empty/run2/MD.Avoca.GZMB.Mm.empty_run2.MD003.sh WorkDir=/vlsci/VR0071/briley/GranzymeB/NAMD2/GZMB.Mm.empty/run2 Block_ID=RMP21Ju171328631 Connection=N,N,N,N Reboot=no Rotate=yes Geometry=1x1x2x4x1 CnloadImage=default MloaderImage=/bgsys/drivers/ppcfloor/boot/firmware IoloadImage=default
#		>	scontrol -o show job all

# parsedjob = Job()
# for item in jobstat.split():
# 	ipart = item.partition('=')
# 	parsedjob[ipart[0]] = ipart[2]
# return parsedjob



