# URL mappings for MD manager main app
from django.conf.urls import patterns, include, url
from manager import views

urlpatterns = patterns('',
   	url(r'^$', views.index, name='index'),
)