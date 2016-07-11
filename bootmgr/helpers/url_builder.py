from django.core.urlresolvers import reverse


def get_root_url(request):
    return request.build_absolute_uri(reverse('bootmgr:index', args=()))


def get_connect_url(request, host_id=None, mac_address=None, uuid=None):
    if host_id:
        return request.build_absolute_uri(reverse('bootmgr:connect',kwargs={'host_id': host_id}))
    elif mac_address and uuid:
        return request.build_absolute_uri(reverse('bootmgr:connect', kwargs={'mac_address': mac_address, 'uuid': uuid}))
    elif mac_address:
        return request.build_absolute_uri(reverse('bootmgr:connect', kwargs={'mac_address': mac_address}))
    elif uuid:
        return request.build_absolute_uri(reverse('bootmgr:connect', kwargs={'uuid': uuid}))
    else:
        return request.build_absolute_uri(reverse('bootmgr:connect')) + '/uuid/${uuid}/mac/${mac:hexhyp}/'


def get_menu_url(request, menuentry_id=None, menu_id=None, host_id=None):

    if menuentry_id:
        args = {'menuentry_id': menuentry_id}
    else:
        args = {'menu_id': menu_id}

    if host_id:
        args['host_id'] = host_id

    return request.build_absolute_uri(reverse('bootmgr:menu', kwargs=args))


def get_action_url(request, action_id, host_id=None):
    if action_id and host_id:
        return request.build_absolute_uri(reverse('bootmgr:action',kwargs={'action_id': action_id, 'host_id': host_id}))
    else:
        return request.build_absolute_uri(reverse('bootmgr:action',kwargs={'action_id': action_id}))