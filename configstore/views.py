from django.template import Template, RequestContext
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404

from netbootmgr.hostdb.models import Host
from netbootmgr.configstore.models import ConfigTemplate


def get_config(request, cfg_name,  host_id):

    host = get_object_or_404(Host, pk=host_id)
    cfg = get_object_or_404(ConfigTemplate, name=cfg_name)
    site = get_current_site(request)

    return HttpResponse(content=cfg.render_for_host(host=host, site=site, request=request), content_type=cfg.mime_type)


def index(request):
    bar = {'jack': 4098, 'sape': 4139}
    t = Template("fu foo fooo foo 1 {{ CS.jack }} 2 {{ CS.sape }} 3 {{ CS.jak }}")
    c = RequestContext(request, {'CS': bar})
    return HttpResponse(t.render(c), content_type="text/plain")