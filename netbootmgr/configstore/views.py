from django.template import Template, RequestContext
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404

from netbootmgr.hostdb.models import Host
from netbootmgr.configstore.models import ConfigTemplate


def get_config(request, cfg_name=None, cfg_id=None, host_id=None):
    host = get_object_or_404(Host, pk=host_id)
    cfg = get_object_or_404(ConfigTemplate, name=cfg_name)
    site = get_current_site(request)

    return HttpResponse(content=cfg.render_for_host(host=host, site=site, request=request), content_type=cfg.mime_type)


def index(request):
    pass