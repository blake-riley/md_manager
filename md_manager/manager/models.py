from django.db import models
from django.contrib.auth.models import User

class ClusterHost(models.Model):
	name = models.CharField(max_length=200)
	username = models.CharField(max_length=200)
	hostname = models.CharField(max_length=200)
	qstat_cmd = models.CharField(max_length=200)

	def __unicode__(self):
		return "{0}@{1}".format(self.username, self.hostname)

class SoftwareConfig(models.Model):
	name = models.CharField(max_length=100)
	cluster = models.ForeignKey(ClusterHost)

	def __unicode__(self):
		return "{0}@{1}".format(self.name, self.cluster)

class Project(models.Model):
	name = models.CharField(max_length=200)
	notes = models.CharField(max_length=1000, blank=True)
	## All simulaiton parameters should be stored here.
	simulation_package = models.ForeignKey(SoftwareConfig)

	def __unicode__(self):
		return "{0} :: {1}".format(self.id, self.name)


class Simulation(models.Model):
	name = models.CharField(max_length=200)
	job_uuid = models.CharField(max_length=200)
	last_known_jobid = models.CharField(max_length=20, blank=True)
	project = models.ForeignKey(Project)
	assigned_cluster = models.ForeignKey(ClusterHost)
	work_dir = models.CharField(max_length=400) ## Absolute location
	state = models.CharField(max_length=20, blank=True) ## Active, Idle, Failed, Completed
	notes = models.CharField(max_length=400, blank=True)

	start_time = models.DateTimeField(auto_now_add=True)
	estimated_completion = models.DateTimeField(blank=True)
	progression = models.CharField(max_length=20, blank=True)
	simulation_rate = models.CharField(max_length=20, blank=True) ## ns/day
	n_cores = models.IntegerField(blank=True)
	last_status_update = models.DateTimeField(auto_now=True)


	def __unicode__(self):
		return "{0} :: {1}-{2}".format(self.id, self.project.name, self.name)


class UserProfile(models.Model):
	user = models.OneToOneField(User)

	def __unicode__(self):
		return self.user.username

