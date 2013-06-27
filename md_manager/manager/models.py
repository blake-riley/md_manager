from django.db import models
from django.contrib.auth.models import User

class ClusterHost(models.Model):
	name = models.CharField(max_length=200)
	username = models.CharField(max_length=200)
	hostname = models.CharField(max_length=200)
	qstat_cmd = models.CharField(max_length=200)

	def __unicode__(self):
		return "{0}@{1}".format(self.username, self.hostname)


class UserProfile(models.Model):
	user = models.OneToOneField(User)

	def __unicode__(self):
		return self.user.username

