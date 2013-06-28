# URL mappings for MD manager main app
from django.conf.urls import patterns, include, url
from manager import views

urlpatterns = patterns('',
   	url(r'^$', views.IndexView.as_view(), name='index'),
   	url(r'^active_jobs$', views.active_jobs, name='active_jobs'),
   	url(r'^active_simulations$', views.active_simulations, name='active_simulations'),
   	url(r'^create_simulation$', views.create_simulation, name='create_simulation'),
)