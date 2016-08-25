from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^boot/', include('netbootmgr.bootmgr.urls')),
    url(r'^hostdb/', include('netbootmgr.hostdb.urls')),
    url(r'^configstore/', include('netbootmgr.configstore.urls')),
    url(r'^', admin.site.urls),
]
