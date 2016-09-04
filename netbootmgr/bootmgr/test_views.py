from django.test import TestCase
from django.http import HttpRequest, Http404
from netbootmgr.bootmgr.models import SiteConfig
from netbootmgr.bootmgr import views


class BootManagerNoSiteConnectTest(TestCase):

    request = None

    def setUp(self):
        self.request = HttpRequest()
        self.request.META['SERVER_NAME'] = "boot.example.org"
        self.request.META['SERVER_PORT'] = 80

    def test_connect_without_site(self):
        with self.assertRaises(SiteConfig.DoesNotExist, msg='SiteConfig exists when it should not.'):
            SiteConfig.objects.get(url='http://boot.example.org/boot/')

        with self.settings(BOOTMGR_AUTO_CREATE_NEW_SITES=False):
            with self.assertRaises(Http404, msg='connect view allowed new site creation while disabled.'):
                response = views.connect(request=self.request)

        with self.settings(BOOTMGR_AUTO_CREATE_NEW_SITES=True):
            response = views.connect(request=self.request)
            self.assertEqual(response.status_code, 200, 'connect without url did not return http 200.')
            self.assertEqual(response.content,
                             b'#!ipxe\r\n\r\nchain --autofree --replace ' +
                             b'http://boot.example.org/boot/connect/uuid/${uuid}/mac/${mac:hexhyp}/ || exit',
                             'connect redirect on simple connect was not rendered as expected')
            self.site_config = SiteConfig.objects.get(url='http://boot.example.org/boot/')
            self.assertEqual(self.site_config.url, 'http://boot.example.org/boot/',
                             'site_config was not created as expected.')


class BootManagerConnectTest(TestCase):
    request = None
    site_config = None

    def setUp(self):
        self.request = HttpRequest()
        self.request.META['SERVER_NAME'] = "boot.example.org"
        self.request.META['SERVER_PORT'] = 80

        self.site_config = SiteConfig.objects.create(url='http://boot.example.org/boot/', name='test_site')
        self.site_config.auto_create_hosts = True

    def test_connect_without_params(self):

        with self.settings(BOOTMGR_AUTO_CREATE_NEW_SITES=True):
            response = views.connect(request=self.request)
            self.assertEqual(response.status_code, 200, 'connect without url did not return http 200.')
            self.assertEqual(response.content,
                             b'#!ipxe\r\n\r\nchain --autofree --replace ' +
                             b'http://boot.example.org/boot/connect/uuid/${uuid}/mac/${mac:hexhyp}/ || exit',
                             'connect redirect on simple connect was not rendered as expected')
            self.site_config = SiteConfig.objects.get(url='http://boot.example.org/boot/')
            self.assertEqual(self.site_config.url, 'http://boot.example.org/boot/',
                             'site_config was not created as expected.')

    def test_connect_invalid_host_id(self):
        with self.assertRaises(Http404, msg='connect view allowed incorrect host_id.'):
            response = views.connect(request=self.request, host_id="a12")

        with self.assertRaises(Http404, msg='connect view allowed incorrect host_id.'):
            response = views.connect(request=self.request, host_id="1.2")

        with self.assertRaises(Http404, msg='connect view allowed incorrect host_id.'):
            response = views.connect(request=self.request, host_id="1,0")

    def test_connect_with_unknown_host_id(self):
        with self.assertRaises(Http404, msg='connect view allowed unknown host_id.'):
            response = views.connect(request=self.request, host_id="1337")

    def test_connect_with_invalid_mac(self):
        with self.assertRaises(Http404, msg='connect view allowed invalid mac address.'):
            response = views.connect(request=self.request, mac_address="00-00-00-00-0G")

        with self.assertRaises(Http404, msg='connect view allowed invalid mac address.'):
            response = views.connect(request=self.request, mac_address="00-00-00-00")

        with self.assertRaises(Http404, msg='connect view allowed invalid mac address.'):
            response = views.connect(request=self.request, mac_address="00:00:00:00:01")

        with self.assertRaises(Http404, msg='connect view allowed invalid mac address.'):
            response = views.connect(request=self.request, mac_address="00 00 00 00 01")

        with self.assertRaises(Http404, msg='connect view allowed invalid mac address.'):
            response = views.connect(request=self.request, mac_address="00-00-00- 0-01")

    def test_connect_with_valid_mac(self):
        response = views.connect(request=self.request, mac_address="00-00-00-00-01")
        response = views.connect(request=self.request, mac_address="0000000001")

    def test_connect_incorrect_params(self):
        pass
        #response = views.connect(request=self.request, host_id="12")