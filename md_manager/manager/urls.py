# URL mappings for MD manager main app
from django.conf.urls import patterns, include, url
from manager import views

urlpatterns = patterns('',
   	url(r'^$', views.IndexView.as_view(), name='index'),
   	url(r'^cluster_status$', views.cluster_status, name='cluster_status'),
   	url(r'^view_simulations$', views.view_simulations, name='view_simulations'),
   	url(r'^update_simulations$', views.update_simulations, name='update_simulations'),
   	url(r'^create_simulation$', views.create_simulation, name='create_simulation'),
)