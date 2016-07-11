from django.conf.urls import url

from netbootmgr.configstore import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<cfg_name>[^/]+)/host/(?P<host_id>[^/]+)', views.get_config, name='cfg-name-host'),
    url(r'^(?P<cfg_name>[^/]+)', views.get_config, name='cfg-name'),
    url(r'^(?P<cfg_uuid>[^/]+)/host/(?P<host_id>[^/]+)', views.get_config, name='cfg-uuid-host'),
    url(r'^(?P<cfg_uuid>[^/]+)', views.get_config, name='cfg-uuid'),
]