from django.http import Http404, HttpResponse
from django.conf import settings
from netbootmgr.bootmgr.helpers.bootmgr import BootManager
from netbootmgr.bootmgr.models import SiteConfig, Action, Menu, MenuEntry
from netbootmgr.hostdb.models import Host
import re


def connect(request, host_id=None, mac_address=None, uuid=None):

    # stop if host id was set and has invalid format
    if host_id and re.compile('^\d+$').match(host_id) is None:
        raise Http404('Host ID is invalid.')

    # stop if mac address was set and has invalid format
    if mac_address and re.compile('^[a-fA-F0-9_-]+$').match(mac_address) is None:
        raise Http404('Mac Address is invalid.')

    if mac_address and not len(mac_address) == 14 and not len(mac_address) == 10:
        raise Http404('Mac Address has incorrect length.')

    # stop if ipxe_uuid was set and has invalid format
    if uuid and re.compile('^[a-zA-Z0-9_-]+$').match(uuid) is None:
        raise Http404('UUID is invalid.')

    # stop if not site config can be found or created
    try:
        auto_create_sites = getattr(settings, 'BOOTMGR_AUTO_CREATE_NEW_SITES', False)
        site_config, created = SiteConfig.get_or_create_from_request(request, auto_create_sites)
    except SiteConfig.DoesNotExist:
        raise Http404('SiteConfig not found.')

    # try to initiate boot manager and connect using the given parameters
    try:
        boot_manager = BootManager(request, site_config=site_config)
        boot_manager.connect(host_id=host_id, mac=mac_address, uuid=uuid)
    except Host.DoesNotExist:
        raise Http404("Host does not exist and could not be created.")
    except BootManager.HostRedirectRequired:
        return HttpResponse(content=boot_manager.get_redirect_script(), content_type="text/plain")

    boot_script = boot_manager.get_boot_script()

    return HttpResponse(content=boot_script, content_type="text/plain")


def action(request, action_id, host_id=None):
    # stop if not site config can be found or created
    try:
        site_config = SiteConfig.get_from_request(request)
    except SiteConfig.DoesNotExist:
        raise Http404('SiteConfig not found.')

    if host_id and re.compile('^\d+$').match(host_id) is None:
        raise Http404('Host ID is invalid.')

    if action_id and re.compile('^\d+$').match(action_id) is None:
        raise Http404('Action ID is invalid.')

    # try to initiate boot manager and connect using the given parameters
    boot_manager = BootManager(request, site_config=site_config)
    if host_id:
        try:
            boot_manager.set_host(host_id=host_id)
        except Host.DoesNotExist:
            pass

    try:
        boot_manager.set_action(action_id=action_id)
    except Action.DoesNotExist:
        raise Http404('Action ID not found.')

    boot_script = boot_manager.get_boot_script()

    return HttpResponse(content=boot_script, content_type="text/plain")


def menu(request, menu_id=None, menuentry_id=None, host_id=None):
    # stop if not site config can be found or created
    try:
        site_config = SiteConfig.get_from_request(request)
    except SiteConfig.DoesNotExist:
        raise Http404('SiteConfig not found.')

    if host_id and re.compile('^\d+$').match(host_id) is None:
        raise Http404('Host ID is invalid.')

    if menu_id and re.compile('^\d+$').match(menu_id) is None:
        raise Http404('Menu ID is invalid.')

    if menuentry_id and re.compile('^\d+$').match(menuentry_id) is None:
        raise Http404('MenuEntry ID is invalid.')

    # try to initiate boot manager and connect using the given parameters
    boot_manager = BootManager(request, site_config=site_config)
    if host_id:
        try:
            boot_manager.set_host(host_id=host_id)
        except Host.DoesNotExist:
            pass

    try:
        boot_manager.set_menu(menuentry_id=menuentry_id, menu_id=menu_id)
    except Menu.DoesNotExist:
        raise Http404('Menu ID not found.')
    except MenuEntry.DoesNotExist:
        raise Http404('Menu Entry ID not found.')

    boot_script = boot_manager.get_boot_script()

    return HttpResponse(content=boot_script, content_type="text/plain")


def index(request):
    raise Http404("ipxe_index is not yet implemented.")