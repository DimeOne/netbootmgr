from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

MAX_RECURSION_LEVEL = 5


def create_host_identifiers(host, identifiers):
    for identifier in identifiers:

        if type(identifier) is tuple and len(identifier) >= 2:
            identifier = {'identifier_type': identifier[0], 'identifier': identifier[1]}

        if type(identifier) is dict and ('identifier' and 'identifier_type' in identifier):
            pass


def get_unique_host_identifiers(identifiers):
    from netbootmgr.hostdb.models import UniqueHostIdentifier

    identifier_filter = None

    for identifier in identifiers:

        if type(identifier) is tuple and len(identifier) >= 2:
            identifier = {'identifier_type': identifier[0],'identifier': identifier[1]}

        if type(identifier) is dict and ('identifier' and 'identifier_type' in identifier):

            if identifier_filter is None:
                identifier_filter = Q(**identifier)
            else:
                identifier_filter = Q(identifier_filter | Q(**identifier))

    return UniqueHostIdentifier.objects.all().filter(identifier_filter)


def get_settings_dict(custom_settings):

    custom_settings_dict = {}

    for custom_setting in custom_settings:
        if custom_setting.name not in list(custom_settings_dict.keys()):
            custom_settings_dict[custom_setting.name] = custom_setting.value

    return custom_settings_dict


def get_settings_filter_for_objects(content_objects, add_global=False, object_filter=None):

    for content_object in content_objects:

        if content_object is None:
            new_filter = Q(content_type__isnull=True)
        else:
            new_filter = Q(content_type=ContentType.objects.get_for_model(content_object).id,
                           object_id=content_object.id)

        if object_filter:
            object_filter = Q(object_filter | new_filter)
        else:
            object_filter = new_filter

    if add_global:
        object_filter = Q(object_filter | Q(content_type__isnull=True))

    return object_filter


def render_template(template, context, request=None, recursive=False):
    from django.template import Template, Context, RequestContext

    if request:
        context = RequestContext(request, context)
    else:
        context = Context(context)

    if recursive:
        for x in range(1,MAX_RECURSION_LEVEL):
            rendered_template = Template(template).render(context)

            if rendered_template == template:
                return rendered_template

            template = rendered_template

    return Template(template).render(context)


def render_host_template(template, request=None, host=None, settings=None, site_config=None, fallback_objects=None,
                         recursive=False):

    if settings is None:
        final_fallback_objects = []
        if site_config:
            final_fallback_objects = [site_config]
        if fallback_objects:
            final_fallback_objects += fallback_objects
        if host:
            final_fallback_objects = host.get_custom_setting_filter_objects() + final_fallback_objects

        from netbootmgr.hostdb.models import CustomSetting
        settings = get_settings_dict(
            CustomSetting.objects.filter(
                get_settings_filter_for_objects(final_fallback_objects, add_global=True)))

    context = {'host': host, 'settings': settings, 'site_config': site_config, 'request': request}

    return render_template(template=template, context=context, request=request, recursive=recursive)

