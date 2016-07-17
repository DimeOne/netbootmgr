from django.test import TestCase
from netbootmgr.hostdb.models import *
from netbootmgr.hostdb.helpers import *


class HostRenderTestCase(TestCase):
    host = None
    site = None
    group = None

    def setUp(self):
        self.host = Host.objects.create(name="HostTestHost", hostname="HostTestHostname")
        self.group = Group.objects.create(name="CustomSettingsGroup", )
        self.group.hosts.add(self.host)

    def test_render_host(self):
        self.assertEqual(render_host_template(host=self.host, template="{{ host.name }}"), "HostTestHost",
                         "host.name was not rendered correctly")

    def test_render_hostname(self):
        self.assertEqual(render_host_template(host=self.host, template="{{ host.hostname }}"), "HostTestHostname",
                         "host.hostname was not rendered correctly")


class UniqueHostIdentifierTestCase(TestCase):

    uuid = [
        'a16f6a62-a31b-4df2-96bc-c958e162c560',
        'cc8aedea-41ec-4fbf-bdc4-ebc190800bdb',
        '7565d12f-9f51-4e2f-b2e7-8a07df5422ae',
        'ef898006-7ea0-4054-aa08-9e08c907896d'
    ]
    mac = [
        '00-00-00-00-00-01',
        '00-00-00-00-00-02',
        '00-00-00-00-00-03',
        '00-00-00-00-00-04',
    ]
    host_names_short = ['ch1', 'wh1', 'wh2']
    host_names = ['Correct Host 1', 'Wrong Host 1', 'Wrong Host 2']

    def setUp(self):

        hosts = [
            Host.objects.create(name_short=self.host_names_short[0], name=self.host_names[0]),
            Host.objects.create(name_short=self.host_names_short[1], name=self.host_names[1]),
            Host.objects.create(name_short=self.host_names_short[2], name=self.host_names[2])
        ]

        uuid_unique_identifiers = [
            UniqueHostIdentifier.objects.create(identifier_type='uuid', identifier=self.uuid[0], host=hosts[0]),
            UniqueHostIdentifier.objects.create(identifier_type='uuid', identifier=self.uuid[1], host=hosts[1]),
            UniqueHostIdentifier.objects.create(identifier_type='uuid', identifier=self.uuid[2], host=hosts[2])
        ]

        mac_unique_identifiers = [
            UniqueHostIdentifier.objects.create(identifier_type='mac', identifier=self.mac[0], host=hosts[0]),
            UniqueHostIdentifier.objects.create(identifier_type='mac', identifier=self.mac[1], host=hosts[1]),
            UniqueHostIdentifier.objects.create(identifier_type='mac', identifier=self.mac[2], host=hosts[2])
        ]

    def test_get_host_by_uuid(self):

        unique_identifier = UniqueHostIdentifier.objects.all().filter(identifier_type='uuid', identifier=self.uuid[0])

        assert len(unique_identifier) == 1, 'Incorrect number of unique identifiers returned using UUID'
        assert unique_identifier[0].host.name_short == self.host_names_short[0], 'Host could not be found using UUID'

    def test_get_host_by_mac(self):

        unique_identifier = UniqueHostIdentifier.objects.all().filter(identifier_type='mac', identifier=self.mac[0])

        assert len(unique_identifier) == 1, 'Incorrect number of unique identifiers returned using MAC'
        assert unique_identifier[0].host.name_short == self.host_names_short[0], 'Host could not be found using MAC'

    def test_get_host_by_uuid_and_mac_tuple_and_dict(self):

        identifier_tuples = (
            ('uuid', self.uuid[0]),
            ('mac', self.mac[0])
        )

        identifier_dicts = (
            {'identifier_type': 'uuid', 'identifier': self.uuid[0]},
            {'identifier_type': 'mac', 'identifier': self.mac[0]}
        )

        tuple_identifiers = get_unique_host_identifiers(identifier_tuples)
        assert len(tuple_identifiers) == 2, 'Incorrect number of unique identifiers returned using tuple'
        for identifier in tuple_identifiers:
            assert identifier.host.name_short == self.host_names_short[0], \
                'Incorrect Host returned using tuple and {0}={1}'.format(identifier.identifier_type,
                                                                         identifier.identifier)

        dict_identifiers = get_unique_host_identifiers(identifier_dicts)
        assert len(dict_identifiers) == 2, 'Incorrect number of unique identifiers returned using dict'
        for identifier in dict_identifiers:
            assert identifier.host.name_short == self.host_names_short[0], \
                'Incorrect Host returned using dict and {0}={1}'.format(identifier.identifier_type,
                                                                        identifier.identifier)

    def test_get_host_by_uuid_or_mac(self):

        identifier_dicts_uuid = (
            {'identifier_type': 'uuid', 'identifier': self.uuid[0]},
            {'identifier_type': 'mac', 'identifier': self.mac[3]}
        )

        identifier_dicts_mac = (
            {'identifier_type': 'uuid', 'identifier': self.uuid[3]},
            {'identifier_type': 'mac', 'identifier': self.mac[0]}
        )

        identifiers = get_unique_host_identifiers(identifier_dicts_uuid)
        assert len(identifiers) == 1, 'Incorrect number of unique identifiers returned using incorrect mac'
        for identifier in identifiers:
            assert identifier.host.name_short == self.host_names_short[0], \
                'Incorrect Host returned using tuple and {0}={1}'.format(identifier.identifier_type,
                                                                         identifier.identifier)

        identifiers = get_unique_host_identifiers(identifier_dicts_mac)
        assert len(identifiers) == 1, 'Incorrect number of unique identifiers returned using incorrect uuid'
        for identifier in identifiers:
            assert identifier.host.name_short == self.host_names_short[0], \
                'Incorrect Host returned using dict and {0}={1}'.format(identifier.identifier_type,
                                                                        identifier.identifier)


class CustomSettingsTestCase(TestCase):

    host = None
    group = None
    os = None
    common_identifier = None

    def setUp(self):
        self.host = Host.objects.create(name_short="TH1", name="Test Host 01")
        self.group = Group.objects.create(name="TG01")
        self.group.hosts.add(self.host)
        self.os = OperatingSystem.objects.create(name_short='w7', name='Windows 7', version="12")

        CustomSetting.objects.create(content_object=self.os, name="test_order_setting", value='os')
        CustomSetting.objects.create(content_object=self.group, name='test_order_setting', value='group')
        CustomSetting.objects.create(content_object=self.host, name="test_order_setting", value='host')
        CustomSetting.objects.create(name="test_order_setting", value='global')

    def test_custom_settings_valid_order(self):

        # host > group > os > global
        setting_filter = get_settings_filter_for_objects([self.host, self.group, self.os, None])
        custom_settings = CustomSetting.objects.all().filter(setting_filter)
        setting_dict = get_settings_dict(custom_settings)
        assert custom_settings.count() == 4, "incorrect amount of custom settings received"
        assert "test_order_setting" in setting_dict.keys(), \
            "key test_setting not found in setting_dict"
        assert setting_dict["test_order_setting"] == "host", \
            "incorrect custom setting value returned - order does not match"

        # global > os > group > host
        setting_filter = get_settings_filter_for_objects([None, self.os, self.group, self.host ])
        custom_settings = CustomSetting.objects.all().filter(setting_filter)
        setting_dict = get_settings_dict(custom_settings)
        assert custom_settings.count() == 4, "incorrect amount of custom settings received"
        assert "test_order_setting" in setting_dict.keys(), \
            "key test_setting not found in setting_dict"
        assert setting_dict["test_order_setting"] == "global", \
            "incorrect custom setting value returned - order does not match"


class CustomSettingsRenderTestCase(TestCase):

    def setUp(self):

        os = OperatingSystem.objects.create(name="Test OS", name_short="test1", version=0)
        common_identifier = CommonIdentifier.objects.create(identifier_type='model', identifier='test_id')

        host = Host.objects.create(name="CustomSettingsHost", hostname="CustomUniqueIdentifierHost", os=os)
        host.common_identifiers.add(common_identifier)
        host_recursion = Host.objects.create(name="CustomSettingsHostRecursion", hostname="CustomSettingsRecursionHost")

        group = Group.objects.create(name="CustomSettingsGroup", )
        group.hosts.add(host)
        group_other = Group.objects.create(name="CustomSettingsGroup2", )
        group_other.hosts.add(host)

        # create objects to create custom_site settings for, that should not appear
        host_bad = Host.objects.create(name="CustomSettingsHostBad", hostname="CustomUniqueIdentifierHost")
        group_bad = Group.objects.create(name="CustomSettingsGroupBad", )
        group_bad.hosts.add(host_bad)

        # correct custom_site settings
        CustomSetting.objects.create(content_object=host,
                                     name="host_setting", value='bar')
        CustomSetting.objects.create(content_object=os,
                                     name="os_setting", value='bar')
        CustomSetting.objects.create(content_object=common_identifier,
                                     name="common_setting", value='bar')
        CustomSetting.objects.create(content_object=group,
                                     name='group_setting', value='bar')
        CustomSetting.objects.create(content_object=group_other,
                                     name='group_other_setting', value='bar')
        CustomSetting.objects.create(name="global_setting", value='bar')

        # custom_site settings for non related hosts, groups or sites should not appear
        CustomSetting.objects.create(content_object=host_bad,
                                     name='wrong_host_setting', value='wrong host')
        CustomSetting.objects.create(content_object=group_bad,
                                     name='wrong_group_setting', value='wrong group')

        # custom_site settings should be resolved in order: host > os > groups > common ids > global
        # these settings should not appear
        CustomSetting.objects.create(content_object=os,
                                     name="host_setting", value='wrong scope - os >  host')
        CustomSetting.objects.create(content_object=common_identifier,
                                     name="host_setting", value='wrong scope - common id > host')
        CustomSetting.objects.create(content_object=group,
                                     name="host_setting", value='wrong scope - group > host')
        CustomSetting.objects.create(name="host_setting", value='wrong scope - global > host')

        CustomSetting.objects.create(content_object=common_identifier,
                                     name="os_setting", value='wrong scope - common id > os')
        CustomSetting.objects.create(content_object=group,
                                     name="os_setting", value='wrong scope - group > os')
        CustomSetting.objects.create(name="os_setting", value='wrong scope - global > os')

        # CustomSetting.objects.create(name="assertError", value='assertErrorsCanBeThrown')
        CustomSetting.objects.create(content_object=host_recursion, name="level_1_", value='bar')
        offset = 2
        for x in range(offset, MAX_RECURSION_LEVEL+offset):
            CustomSetting.objects.create(content_object=host_recursion,
                                         name="level_{}_".format(x), value='{{{{ settings.level_{}_ }}}}'.format(x-1))

    def test_custom_settings(self):
        host = Host.objects.get(name="CustomSettingsHost")

        # non distinct list of all matching custom_site settings
        custom_settings = host.get_custom_settings()

        settings_dict = get_settings_dict(custom_settings)

        for setting_name in list(settings_dict.keys()):
            # print(setting_name)
            self.assertEqual(settings_dict[setting_name], 'bar',
                             'custom setting exists that should not be there: {} - {}'.format(
                                 setting_name, settings_dict[setting_name]))

        self.assertEqual(len(settings_dict.keys()), 6, "there should only be 6 keys in custom settings dict")

    def test_custom_settings_render_recursive(self):
        host = Host.objects.get(name="CustomSettingsHostRecursion")

        rendered_template = render_host_template(template='{{ settings.level_1_ }}', host=host, recursive=False)
        self.assertEqual('bar', rendered_template, "level 1 setting was not rendered recursively at level 1")

        rendered_template = render_host_template(template='{{{{ settings.level_{}_ }}}}'.format(MAX_RECURSION_LEVEL),
                                                 host=host, recursive=True)
        self.assertEqual('bar', rendered_template,
                         "level {} setting not was rendered recursively".format(MAX_RECURSION_LEVEL))

