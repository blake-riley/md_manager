#	Ben's required returns:

get_status()
return host_list
-	list host_list []
	-	tuple ()
		-	str host
		-	list status []
			-	int active_jobs
			-	int total_jobs
			-	int active_procs
			-	int total_procs
			-	float percentage_active
		-	list job_list []
			-	dict job_dict {}
				-	'job_id' = int
				-	'job_name' = str
				-	'job_owner' = str
				-	'nodes' = int
				-	'n_nodes' = int
				-	'state' = str
				-	'cores' = int
				-	'work_dir' = str


#	My structure:

-	list host_list []			#	Not implemented
	-	class __Host__

__Host__.get_status()
return self.cluster_status, self.job_list
-	dict cluster_status {}
	-	'procs' = dict {}
		-	'alloc' = int
		-	'idle' = int
		-	'other' = int
		-	'total' = int
	-	'nodes' = dict {}
		-	'alloc' = int
		-	'idle' = int
		-	'other' = int
		-	'total' = int
	-	'last_updated' = float
-	dict job_list
	-	key job_id = class __Job__(dict) {}
		-	'jobid' = str
		-	'last_updated' = float
		-	'jobname' = str
		-	'exec_host' = str
		-	'account' = str
		-	'username' = str
		-	'userid' = str
		-	'group' = str
		-	'groupid' = str
		-	'nodes' = str
		-	'cpus' = str
		-	'jobstate' = str
		-	'time_start' = str
		-	'time_end' = str
		-	'time_limit' = str
		-	'time_running' = str
		-	'time_remaining' = str
		-	'comment' = str
		-	'geometry' = str