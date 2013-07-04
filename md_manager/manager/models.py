from django.db import models
from django.contrib.auth.models import User

class ClusterHost(models.Model):
	name = models.CharField(max_length=200)
	username = models.CharField(max_length=200)
	hostname = models.CharField(max_length=200)
	qstat_cmd = models.CharField(max_length=200)

	def __unicode__(self):
		return "{0}@{1}".format(self.username, self.hostname)

class Project(models.Model):
	name = models.CharField(max_length=200)
	notes = models.CharField(max_length=1000, blank=True)
	base_dir = models.CharField(max_length=400)
	## All simulaiton parameters should be stored here.

	## simulation_package = models.ForeignKey(SoftwareConfig)



	def __unicode__(self):
		return "{0} :: {1}".format(self.id, self.name)


class Simulation(models.Model):
	name = models.CharField(max_length=200)
	job_uuid = models.CharField(max_length=200)
	last_known_jobid = models.CharField(max_length=20, blank=True)
	project = models.ForeignKey(Project)
	assigned_cluster = models.ForeignKey(ClusterHost)
	work_dir = models.CharField(max_length=400) ## Relative or absolute to the project base_dir
	state = models.CharField(max_length=20, blank=True) ## Active, Idle, Failed, Completed

	## Start date/time
	## Estimated completion time
	## Completed date/time
	## Simulation rate (ns/day)
	## nodes, ppn, total cores


	def __unicode__(self):
		return "{0} :: {1}-{2}".format(self.id, self.project.name, self.name)


class UserProfile(models.Model):
	user = models.OneToOneField(User)

	def __unicode__(self):
		return self.user.username

