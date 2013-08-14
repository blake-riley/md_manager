from django.contrib import admin
from manager.models import *

admin.site.register(UserProfile)
admin.site.register(Simulation)
admin.site.register(SoftwareConfig)
admin.site.register(ClusterHost)
admin.site.register(ClusterJob)
admin.site.register(Project)
admin.site.register(EquilibrationProtocol)
admin.site.register(ProductionProtocol)