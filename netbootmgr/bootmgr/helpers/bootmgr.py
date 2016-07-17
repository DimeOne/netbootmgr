from netbootmgr.hostdb.models import *
from netbootmgr.bootmgr.models import *
from netbootmgr.bootmgr.helpers import url_builder


class BootManagerException(Exception):
    pass


class BootManager:

    def __init__(self, request, site_config, preview=False, host=None, *args,
                 **kwargs):

        self.root_url = url_builder.get_root_url(request)
        self.request = request
        self.preview = preview

        self.site_config = site_config
        self.settings = None
        self.host = None

        from netbootmgr.bootmgr.helpers import ipxe_builder
        self.builder = ipxe_builder
        from netbootmgr.bootmgr.helpers import ipxe_render
        self.render = ipxe_render

        self.redirect_required = False
        self.redirect_url = None

        self.action_source = None
        self.action = None
        self.fallback_action = None
        self.menu = None

        self.boot_script_finalized = False
        self.render_required = False
        self.boot_script = None
        self.rendered_boot_script = None

        if host:
            self.host = host

    def get_site_config(self):
        return self.site_config

    def create_host(self, uuid=None, mac=None):
        from django.utils import timezone
        host_count = Host.objects.all().count()

        desc = "Host was created after booting from {} with AUTO_CREATE_NEW_HOSTS at {}".format(
            self.root_url,
            timezone.now()
        )
        self.host = Host.objects.create(name_short="new_{}".format(host_count),
                                        name="iPXE Generated Host #{0}".format(host_count),
                                        description=desc)

        if uuid:
            UniqueHostIdentifier.objects.create(host=self.host, identifier_type='uuid', identifier=uuid)
        if mac:
            UniqueHostIdentifier.objects.create(host=self.host, identifier_type='mac', identifier=mac)

    def set_host(self, host_id=None, uuid=None, mac=None):

        # use host_id if given
        if host_id:
            self.host = Host.objects.get(pk=host_id)

        # use uuid or mac as host_identifiers to find host
        elif uuid or mac:
            from netbootmgr.hostdb.helpers import get_unique_host_identifiers
            identifiers = []
            if uuid:
                identifiers.append({'identifier_type': 'uuid', 'identifier': uuid})
            if mac:
                identifiers.append({'identifier_type': 'mac', 'identifier': mac})

            self.host = Host.get_from_unique_identifiers(identifiers)

        else:
            # if no host_id or uuid or mac have been given
            self.redirect_required = True
            self.redirect_url = self.get_connect_url()
            raise self.HostRedirectRequired

    def set_or_create_host(self, host_id=None, uuid=None, mac=None):

        try:
            self.set_host(host_id=host_id, uuid=uuid, mac=mac)
        except Host.DoesNotExist:
            if self.site_config.auto_create_hosts:
                self.create_host(uuid=uuid, mac=mac)

                # create host task if site_config has an initial_host_action
                if self.site_config.initial_host_action:
                    HostTask.objects.create()

            else:
                raise Host.DoesNotExist

    def get_host(self):
        return self.host

    def get_custom_settings(self):
        return self.settings

    def get_custom_settings_dict(self):
        from netbootmgr.hostdb.helpers import get_settings_dict
        if self.settings:
            return get_settings_dict(self.settings)

    def set_custom_settings(self):
        if self.settings is None:
            from netbootmgr.hostdb.helpers import get_settings_filter_for_objects
            filter_objects = []
            if self.host:
                filter_objects = self.host.get_custom_setting_filter_objects()

            if self.action:
                filter_objects.append(self.action)
                if self.action.render_type:
                    filter_objects.append(self.action.render_type)
                if self.action.action_category:
                    filter_objects.append(self.action.action_category)

            if self.site_config:
                filter_objects.append(self.site_config)

            self.settings = CustomSetting.objects.filter(
                get_settings_filter_for_objects(content_objects=filter_objects, add_global=True))

    def get_action_source(self):
        return self.action_source

    def get_action(self):
        return self.action

    def set_action(self, action=None, action_id=None, source=None):
        if action:
            self.action = action
        elif action_id:
            self.action_source = ('action_id', action_id)
            self.action = Action.objects.get(pk=action_id)

        if source:
            self.action_source = source

    def set_action_from_host(self):
        try:
            host_task = self.host.hosttask_set.all()[:1].get()
            self.action = host_task.action
            self.action_source = host_task
            return True
        except HostTask.DoesNotExist:
            pass

        try:
            fallback = FallbackAction.objects.get(content_type=ContentType.objects.get_for_model(Host).id,
                                                  object_id=self.host.id)
            self.fallback_action = fallback.action
            return True
        except FallbackAction.DoesNotExist:
            pass

    def get_menu(self):
        return self.menu

    def set_menu(self, menu=None, menu_id=None, menuentry_id=None, source=None):

        if menu:
            self.menu = menu
        elif menu_id:
            self.menu = Menu.objects.get(pk=menu_id)
        elif menuentry_id:
            menu_entry = MenuEntry.objects.get(id=menuentry_id)
            if isinstance(menu_entry.content_object, Action):
                self.action = menu_entry.content_object
                self.action_source = menu_entry
            elif isinstance(menu_entry.content_object, Menu):
                self.menu = menu_entry.content_object

    def set_redirect_url(self, url=None):
        if url:
            self.redirect_url = url
        self.redirect_required = True

    def build_boot_menu_script(self):

        if self.host:
            host_id = self.host.id
        else:
            host_id = None

        if self.fallback_action:
            menu_fallback_action = self.fallback_action
        elif self.site_config.timeout_action:
            menu_fallback_action = self.site_config.timeout_action
        else:
            menu_fallback_action = None

        self.boot_script = self.render.get_boot_menu_script(
            request=self.request,
            builder=self.builder,
            menu=self.menu,
            back_menu=self.site_config.menu,
            host_id=host_id,
            timeout_s=self.site_config.menu_timeout,
            fallback_action=menu_fallback_action,
            reload_delay_s=self.site_config.reload_delay,
            reconnect_delay_s=self.site_config.reconnect_delay,
            auto_reload=self.site_config.auto_reload,
            show_reconnect=self.site_config.show_reconnect
        )

    def build_boot_script(self):

        if self.action:
            self.boot_script = self.render.get_boot_action_script(builder=self.builder, action=self.action)
        elif self.fallback_action and not self.site_config.show_menu_fallback:
            self.boot_script = self.render.get_boot_action_script(builder=self.builder, action=self.fallback_action)
        elif self.menu:
            self.build_boot_menu_script()
        else:
            self.boot_script = self.builder.echo("No Action or Menu could be found for this host or site.")

        self.render_boot_script()
        self.finalize_boot_script()

    def render_boot_script(self):

        self.set_custom_settings()

        self.rendered_boot_script = self.render.render_boot_script(
            request=self.request,
            host=self.host,
            script=self.boot_script,
            site_config=self.site_config,
            settings=self.get_custom_settings_dict()
        )
        self.render_required = False

    def finalize_boot_script(self):
        if self.boot_script_finalized:
            raise BootManager.BootScriptFinalized
        self.boot_script_finalized = True

        if self.preview is False and self.action_source and isinstance(self.action_source, HostTask):
            self.action_source.delete()

    def get_redirect_script(self):
        if self.redirect_required and self.redirect_url:
            return self.builder.get_header() + self.builder.if_not(
                self.builder.redirect(url=self.redirect_url, auto_free=True, replace=True),
                self.builder.get_exit(newline=False),
            )
        return self.builder.get_header() + self.builder.if_not(
            self.builder.redirect(url=self.get_connect_url(), auto_free=True, replace=True),
            self.builder.get_exit(newline=False),
        )

    def get_boot_script(self):

        # return redirect script if the bootmanager is set for a redirect
        if self.redirect_required:
            return self.get_redirect_script()

        # if a rendered boot script exists, we do not change it
        elif self.rendered_boot_script:
            return self.builder.get_header() + self.rendered_boot_script

        # if a boot script is finalized but requires rendering we return it rendered
        elif self.boot_script_finalized and self.render_required:
            self.render_boot_script()
            return self.builder.get_header() + self.rendered_boot_script

        # if it does not require finalization we can return unrendered boot script
        elif self.boot_script_finalized:
            return self.builder.get_header() + self.boot_script

        # if we got here, no boot script has been created and we should do it with what we have
        else:
            self.build_boot_script()
            return self.builder.get_header() + self.rendered_boot_script

    def get_connect_url(self):
        return url_builder.get_connect_url(self.request)

    def connect(self, host_id=None, uuid=None, mac=None):

        self.set_or_create_host(host_id=host_id, mac=mac, uuid=uuid)

        # if an action has already been set - work has been done already
        if self.action:
            return

        # try to get host_task or host fallback
        self.set_action_from_host()

        # if a menu is already set we do not use the default site config menu
        if self.menu:
            return

        # try to get menu from site config
        if self.site_config and self.site_config.menu:
            self.set_menu(menu=self.site_config.menu)

    class HostRedirectRequired(BootManagerException):
        pass

    class BootScriptFinalized(BootManagerException):
        pass

    class BootMenuAlreadySet(BootManagerException):
        pass

    class BootActionAlreadySet(BootManagerException):
        pass

