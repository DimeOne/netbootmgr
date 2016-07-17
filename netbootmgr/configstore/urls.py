from django.conf.urls import url

from netbootmgr.configstore import views

urlpatterns = [
    url(r'^(?P<cfg_name>[^/]+)/host/uuid/(?P<uuid>[^/]+)', views.get_config, name='cfg'),
    url(r'^(?P<cfg_name>[^/]+)/host/mac/(?P<mac_address>[^/]+)', views.get_config, name='cfg'),
    url(r'^(?P<cfg_name>[^/]+)/host/uuid/(?P<uuid>[^/]+)/mac/(?P<mac_address>[^/]+)', views.get_config, name='cfg'),
    url(r'^(?P<cfg_name>[^/]+)/host/(?P<host_id>[^/]+)', views.get_config, name='cfg'),
    url(r'^(?P<cfg_name>[^/]+)', views.get_config, name='cfg'),
    url(r'^id/(?P<cfg_id>[^/]+)/host/(?P<host_id>[^/]+)', views.get_config, name='cfg'),
    url(r'^id/(?P<cfg_id>[^/]+)', views.get_config, name='cfg'),
    url(r'^$', views.index, name='index'),
]