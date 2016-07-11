from netbootmgr.bootmgr.helpers import ipxe_builder, url_builder
from netbootmgr.bootmgr.helpers.bootmgr import BootManager
from django.test import TestCase
from netbootmgr.hostdb.models import *
from .models import SiteConfig
from django.http import HttpRequest

NEWLINE = '\r\n'


class SimpleBuilderTestCase(TestCase):
    builder = ipxe_builder

    def setUp(self):
        pass

    def test_ipxe_redirect(self):

        self.assertEqual(
            self.builder.get_header(),
            "#!ipxe" + NEWLINE,
            "ipxe header was not rendered correctly"
        )
        self.assertEqual(
            self.builder.echo('test'),
            NEWLINE + "echo test",
            "ipxe echo was not rendered correctly"
        )
        self.assertEqual(
            self.builder.redirect("https://test", auto_free=True, replace=True),
            NEWLINE + "chain --autofree --replace https://test",
            "ipxe redirect was not rendered correctly"
        )
        self.assertEqual(
            self.builder.if_not(
                self.builder.redirect('https://test', auto_free=True, replace=True),
                self.builder.get_exit(newline=False)
            ),
            NEWLINE + "chain --autofree --replace https://test || exit",
            'ipxe redirect or exit was not rendered correctly'
        )

    def test_ipxe_menu(self):
        pass


class BootManagerUrlBuilderTestCase(TestCase):

    request = None

    def setUp(self):
        self.request = HttpRequest()
        self.request.META['SERVER_NAME'] = "example.org"
        self.request.META['SERVER_PORT'] = 8000

    def test_root_url(self):
        connect_url = url_builder.get_root_url(self.request)
        self.assertEqual(
            connect_url,
            "http://example.org:8000/boot/",
            'ipxe boot connect url is not as expected.'
        )

    def test_connect_url(self):
        connect_url = url_builder.get_connect_url(self.request)
        self.assertEqual(
            connect_url,
            "http://example.org:8000/boot/connect/uuid/${uuid}/mac/${mac:hexhyp}/",
            'ipxe boot connect url is not as expected.'
        )

    def test_host_connect_url(self):
        host_connect_url = url_builder.get_connect_url(self.request, host_id=1)
        self.assertEqual(
            host_connect_url,
            "http://example.org:8000/boot/connect/host/1",
            'ipxe host connect url is not as expected.'
        )

    def test_mac_connect_url(self):
        host_connect_url = url_builder.get_connect_url(self.request, mac_address=1)
        self.assertEqual(
            host_connect_url,
            "http://example.org:8000/boot/connect/mac/1",
            'ipxe mac connect url is not as expected.'
        )

    def test_uuid_connect_url(self):
        host_connect_url = url_builder.get_connect_url(self.request, uuid=1)
        self.assertEqual(
            host_connect_url,
            "http://example.org:8000/boot/connect/uuid/1",
            'ipxe uuid connect url is not as expected.'
        )

    def test_uuid_mac_connect_url(self):
        host_connect_url = url_builder.get_connect_url(self.request, mac_address=1, uuid=1)
        self.assertEqual(
            host_connect_url,
            "http://example.org:8000/boot/connect/uuid/1/mac/1",
            'ipxe both connect url is not as expected.'
        )

    def test_menu_url(self):
        menu_url = url_builder.get_menu_url(self.request, menuentry_id=1)
        self.assertEqual(
            menu_url,
            "http://example.org:8000/boot/menuentry/1",
            'ipxe menu url is not as expected.'
        )

    def test_host_menu_url(self):
        menu_url = url_builder.get_menu_url(self.request, menuentry_id=1, host_id=1)
        self.assertEqual(
            menu_url,
            "http://example.org:8000/boot/menuentry/1/host/1",
            'ipxe menu url is not as expected.'
        )

    def test_action_url(self):
        action_url = url_builder.get_action_url(self.request, action_id=1)
        self.assertEqual(
            action_url,
            "http://example.org:8000/boot/action/1",
            'ipxe action url is not as expected.'
        )

    def test_host_action_url(self):
        action_url = url_builder.get_action_url(self.request, action_id=1, host_id=1)
        self.assertEqual(
            action_url,
            "http://example.org:8000/boot/action/1/host/1",
            'ipxe action url is not as expected.'
        )


class BootManagerErrorTestCase(TestCase):

    request = None

    def setUp(self):

        self.bad_request = HttpRequest()
        self.bad_request.META['SERVER_NAME'] = "badsite.example.org"
        self.bad_request.META['SERVER_PORT'] = 8001
        self.bad_site_config, self.bad_site_created = SiteConfig.get_or_create_from_request(
            self.bad_request,
            create_new_sites=True
        )
        self.bad_site_config.auto_create_hosts = False
        self.bad_site_config.save()

    def test_site_creation(self):
        self.assertEqual(self.bad_site_created, True, "site_config was not created.")
        self.assertEqual(self.bad_site_config.auto_create_hosts, False, "auto create hosts should be disabled.")

    """
    Host.DoesNotExist should be thrown,
    when trying to set_host with unknown mac and uuid if site_config create_new_hosts is False
    """
    def test_host_creation(self):
        boot_manager = BootManager(request=self.bad_request, site_config=self.bad_site_config)

        with self.assertRaises(Host.DoesNotExist):
            boot_manager.connect(uuid="5", mac="aa-bb-cc-dd-ee-ff")


class BootManagerTestCase(TestCase):

    request = None

    def setUp(self):

        #self.request = HttpRequest()
        #self.request.META['SERVER_NAME'] = "test_site"
        #self.request.META['SERVER_PORT'] = 8000

        #self.site_config, self.site_created = SiteConfig.get_or_create_from_request(self.request, create_new_sites=True)
        #self.site_config.auto_create_hosts = True
        #self.site_config.save()

        self.request = HttpRequest()
        self.request.META['SERVER_NAME'] = "localhost12"
        self.request.META['SERVER_PORT'] = 8000
        self.site_config, self.site_created = SiteConfig.get_or_create_from_request(self.request, create_new_sites=True)
        self.site_config.auto_create_hosts = True
        self.site_config.save()

    def test_setup(self):
        self.assertEqual(self.site_created, True, "site_config was not created.")
        self.assertEqual(self.site_config.auto_create_hosts, True, "site_config does not allow auto_create_hosts")

    def test_connect(self):
        boot_manager = BootManager(request=self.request, site_config=self.site_config)
        boot_manager.connect(uuid="5", mac="aa-bb-cc-dd-ee-ff")

        self.assertEqual(1, boot_manager.get_host().id,
                         "bootmgr has invalid host_id after connect with after connect with auto_create_hosts=True")

    def test_auto_create_hosts(self):
        """
        BootManager.HostRedirectRequired should be thrown,
        when trying to set_host without host_id, mac or uuid
        """
        with self.assertRaises(BootManager.HostRedirectRequired):
            boot_manager = BootManager(request=self.request, site_config=self.site_config)
            boot_manager.set_host(uuid="", mac="")

        #
        boot_manager = BootManager(request=self.request, site_config=self.site_config)
        boot_manager.set_or_create_host(uuid="5", mac="aa-bb-cc-dd-ee-ff")
        self.assertEqual(boot_manager.get_host().name, "iPXE Generated Host #0",
                         "Host received has unexpected Name: {0}".format(boot_manager.get_host().name))

        boot_manager = BootManager(request=self.request, site_config=self.site_config)
        boot_manager.set_host(mac="aa-bb-cc-dd-ee-ff")
        self.assertEqual(boot_manager.get_host().name, "iPXE Generated Host #0",
                         "Host received has unexpected Name: {0} - when Queried by MAC"
                         .format(boot_manager.get_host().name))

        boot_manager = BootManager(request=self.request, site_config=self.site_config)
        boot_manager.set_host(uuid=5)
        self.assertEqual(boot_manager.get_host().name, "iPXE Generated Host #0",
                         "Host received has unexpected Name: {0} - when Queried by UUID"
                         .format(boot_manager.get_host().name))

    def test_redirect_ipxe_connect(self):
        boot_manager = BootManager(request=self.request, site_config=self.site_config)
        self.assertEqual(
            boot_manager.get_redirect_script(),
            '#!ipxe\r\n\r\nchain --autofree --replace ' +
            'http://localhost12:8000/boot/connect/uuid/${uuid}/mac/${mac:hexhyp}/ || exit',
            "ipxe redirect not rendered as expected")

        with self.assertRaises(BootManager.HostRedirectRequired):
            boot_manager.set_host()

        self.assertEqual(
            boot_manager.get_redirect_script(),
            '#!ipxe\r\n\r\nchain --autofree --replace ' +
            'http://localhost12:8000/boot/connect/uuid/${uuid}/mac/${mac:hexhyp}/ || exit',
            "ipxe redirect not rendered as expected")

    def test_host_task(self):
        pass

    def test_host_fallback(self):
        pass

    def test_menu(self):
        pass


class SimpleIPXEBuilderTestCase(TestCase):

    def setUp(self):
        from netbootmgr.bootmgr.helpers import ipxe_builder
        self.builder = ipxe_builder

    def test_get_setting(self):

        self.assertEqual(self.builder.get_setting("toll"), "${toll}", "get_setting failed to render correctly.")


class IpxeBuilderTestCase(TestCase):

    def setUp(self):
        from netbootmgr.bootmgr.helpers import ipxe_builder
        self.builder = ipxe_builder
        from django.core.management import call_command
        call_command("loaddata", 'bootmgr',verbosity=0)
        self.request = HttpRequest()
        self.request.META['SERVER_NAME'] = "localhost12"
        self.request.META['SERVER_PORT'] = 8000
        self.site_config, self.site_created = SiteConfig.get_or_create_from_request(self.request, create_new_sites=True)
        self.site_config.auto_create_hosts = True
        self.site_config.save()

    def test_menu_items(self):
        self.assertEqual(
            "item --key u section_name menu title . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . [U]",
            self.builder.menu_item(title="menu title", section="section_name", key='u', newline=False),
            "Menu Item with key was not rendered as expected."
        )

        self.assertEqual(
            "item section_name menu title . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . ",
            self.builder.menu_item(title="menu title", section="section_name", newline=False),
            "Menu Item without key was not rendered as expected."
        )

        self.assertEqual(
            "\r\nitem section_name menu title . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . ",
            self.builder.menu_item(title="menu title", section="section_name", newline=True),
            "Menu Item with newline was not rendered as expected."
        )

    def test_menu_render(self):
        from netbootmgr.bootmgr.helpers import ipxe_render
        from netbootmgr.bootmgr.models import Menu

        menu = Menu.objects.get(id=1)

        script = ipxe_render.get_boot_menu_script(
            request=self.request,
            builder=self.builder,
            menu=menu,
        )

        # self.assertEqual(script,"dummy","dummy message")


class ShortcutTestCase(TestCase):

    def setUp(self):
        pass

    def test_reverse_lookup(self):
        from netbootmgr.bootmgr.helpers.settings import BOOT_MENU_SHORTCUT_CHOICES_DICT

        self.assertEqual(BOOT_MENU_SHORTCUT_CHOICES_DICT['a'], 'A', 'Failed to get reverse lookup for Shortcut: a')
        self.assertEqual(BOOT_MENU_SHORTCUT_CHOICES_DICT['0x01'], 'Ctrl-A',
                         'Failed to get reverse lookup for Shortcut: Ctrl+A')
        self.assertEqual(BOOT_MENU_SHORTCUT_CHOICES_DICT['0x197e'], 'F12',
                         'Failed to get reverse lookup for Shortcut: F12')



