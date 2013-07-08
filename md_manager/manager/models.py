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

class EquilibrationProtocol(models.Model):
	name = models.CharField(max_length=200)
	description = models.CharField(max_length=600, blank=True)


	def __unicode__(self):
		return "{0} :: {1}".format(self.id, self.name)


class ProductionProtocol(models.Model):
	name = models.CharField(max_length=200)
	description = models.CharField(max_length=600, blank=True)

	n_blocks = models.IntegerField(blank=True, null=True)
	steps_per_block = models.IntegerField(blank=True, null=True)

	timestep = models.FloatField(blank=True, null=True) # fs

	ns_per_block = models.FloatField(blank=True, null=True)	## steps_per_block * timestep :: Units of ns
	total_ns = models.FloatField(blank=True, null=True)	## ns_per_block * n_blocks  :: Units of ns

	def __unicode__(self):
		return "{0} :: {1}".format(self.id, self.name)


class Project(models.Model):
	name = models.CharField(max_length=200)
	notes = models.CharField(max_length=1000, blank=True)
	## All simulaiton parameters should be stored here.
	simulation_package = models.ForeignKey(SoftwareConfig, blank=True, null=True)

	equilibration_protocol = models.ForeignKey(EquilibrationProtocol, blank=True, null=True)
	production_protocol = models.ForeignKey(ProductionProtocol, blank=True, null=True)

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
	estimated_completion = models.DateTimeField(blank=True, null=True)
	progression = models.IntegerField(blank=True, null=True)	## ns (completed_blocks * project.production_protocol.ns_per_block)
	simulation_rate = models.FloatField(blank=True, null=True) ## ns/day
	n_cores = models.IntegerField(blank=True, null=True)
	last_status_update = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return "{0} :: {1}-{2}".format(self.id, self.project.name, self.name)







class UserProfile(models.Model):
	user = models.OneToOneField(User)

	def __unicode__(self):
		return self.user.username

