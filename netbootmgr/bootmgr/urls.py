from django.conf.urls import url
from . import views

app_name = 'bootmgr'
urlpatterns = [
    url(r'^action/(?P<action_id>[^/]+)/host/(?P<host_id>[^/]+)', views.action, name='action'),
    url(r'^action/(?P<action_id>[^/]+)', views.action, name='action'),
    url(r'^menu/(?P<menu_id>[^/]+)/host/(?P<host_id>[^/]+)', views.menu, name='menu'),
    url(r'^menu/(?P<menu_id>[^/]+)', views.menu, name='menu'),
    url(r'^menuentry/(?P<menuentry_id>[^/]+)/host/(?P<host_id>[^/]+)', views.menu, name='menu'),
    url(r'^menuentry/(?P<menuentry_id>[^/]+)', views.menu, name='menu'),
    url(r'^host/(?P<host_id>[^/]+)/action/(?P<action_id>[^/]+)', views.action, name='host'),
    url(r'^host/(?P<host_id>[^/]+)/menu/(?P<menu_id>[^/]+)', views.menu, name='host'),
    url(r'^host/(?P<host_id>[^/]+)/menuentry/(?P<menuentry_id>[^/]+)', views.menu, name='host'),
    url(r'^host/(?P<host_id>[^/]+)/', views.connect, name='host'),
    url(r'^connect/uuid/(?P<uuid>[^/]+)/mac/(?P<mac_address>[^/]+)', views.connect, name='connect'),
    url(r'^connect/uuid/(?P<uuid>[^/]+)', views.connect, name='connect'),
    url(r'^connect/mac/(?P<mac_address>[^/]+)', views.connect, name='connect'),
    url(r'^connect/host/(?P<host_id>[^/]+)', views.connect, name='connect'),
    url(r'^connect', views.connect, name='connect'),
    url(r'^[/]*$', views.connect, name='index'),
]