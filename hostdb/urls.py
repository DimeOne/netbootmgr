from django.conf.urls import url
from netbootmgr.hostdb import views

urlpatterns = [
    url(r'^hosts/$', views.HostIndexView.as_view(), name='host_index'),
    url(r'^host/(?P<pk>[0-9]+)$', views.HostDetailView.as_view(), name='host_detail'),
    url(r'^groups/$', views.GroupIndexView.as_view(), name='group_index'),
    url(r'^group/(?P<pk>[0-9]+)$', views.GroupDetailView.as_view(), name='group_detail'),
    url(r'^$', views.index, name='index'),
]