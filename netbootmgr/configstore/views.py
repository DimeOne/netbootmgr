import re
from django.http import Http404, HttpResponse
from netbootmgr.hostdb.models import Host
from netbootmgr.configstore.models import ConfigTemplate
from netbootmgr.bootmgr.models import SiteConfig
from django.shortcuts import get_object_or_404


def get_config(request, cfg_name=None, cfg_id=None, host_id=None, uuid=None, mac_address=None):

    try:
        site_config = SiteConfig.get_from_request(request)
    except SiteConfig.DoesNotExist:
        raise Http404('SiteConfig not found.')

    if host_id and re.compile('^\d+$').match(host_id) is None:
        raise Http404('Host ID is invalid.')

    if cfg_id and re.compile('^\d+$').match(cfg_id) is None:
        raise Http404('CFG ID is invalid.')

    if host_id:
        host = get_object_or_404(Host, pk=host_id)
    elif uuid or mac_address:
        identifiers = []
        if uuid:
            identifiers.append({'identifier_type': 'uuid', 'identifier': uuid})
        if mac_address:
            identifiers.append({'identifier_type': 'mac', 'identifier': mac_address})

        host = Host.get_from_unique_identifiers(identifiers)
    else:
        host = None

    if cfg_id:
        config_template = get_object_or_404(ConfigTemplate, id=cfg_id)
    elif cfg_name:
        config_template = get_object_or_404(ConfigTemplate, name=cfg_name)
    else:
        raise Http404('No Config.')

    return HttpResponse(content=config_template.render_for_host(host=host, site_config=site_config, request=request),
                        content_type=config_template.mime_type)


def index(request):
    pass