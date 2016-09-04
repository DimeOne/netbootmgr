from django.test import TestCase
from django.http import HttpRequest
from netbootmgr.bootmgr.helpers import ipxe_builder
from netbootmgr.bootmgr.models import SiteConfig


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
        # call_command("loaddata", 'demo',verbosity=0)
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
