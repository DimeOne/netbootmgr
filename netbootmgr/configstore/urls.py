from django.conf.urls import url

from netbootmgr.configstore import views

urlpatterns = [
    url(r'^name/(?P<cfg_name>[^/]+)/host/(?P<host_id>[^/]+)', views.get_config, name='cfg'),
    url(r'^name/(?P<cfg_name>[^/]+)', views.get_config, name='cfg'),
    url(r'^id/(?P<cfg_id>[^/]+)/host/(?P<host_id>[^/]+)', views.get_config, name='cfg'),
    url(r'^id/(?P<cfg_id>[^/]+)', views.get_config, name='cfg'),
    url(r'^$', views.index, name='index'),
]