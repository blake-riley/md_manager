from django.contrib import admin
from manager.models import *

admin.site.register(UserProfile)
admin.site.register(Simulation)
admin.site.register(ClusterHost)
admin.site.register(Project)