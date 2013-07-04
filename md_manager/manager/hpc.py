import paramiko
import os

class HPC:
	"""Simplified interface to paramiko to communicate with a cluster over ssh"""

	hostname = None
	username = None
	client = None
	privatekey = None

	def __init__(self, username, hostname):
		self.username = username
		self.hostname = hostname
		self.client = paramiko.SSHClient()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.client.connect(hostname=hostname, username=username, allow_agent=True)


	def get_OutputError(self, command):
		stdin, stdout, stderr = self.client.exec_command(command)
		retout = stdout.read()
		reterr = stderr.read()
		return (retout, reterr)




# orchard = HPC("orchard.med.monash.edu", "ben")

# stdout, stderr = orchard.get_OutputError("ls")

# print stdout