from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from datetime import datetime


class OperatingSystem(models.Model):
    TYPE_CHOICES = getattr(settings, 'HOSTDB_OS_TYPE_CHOICES', (
        ('', 'Unknown'),
        ('windows', 'Windows'),
        ('linux', 'Linux'),
        ('osx', 'Mac OSX'),
    ))
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_short = models.SlugField(max_length=32, unique=True, verbose_name="Label", null=True)
    name = models.CharField(max_length=64, verbose_name="Display Name", default="Unknown")
    os_type = models.CharField(max_length=8, choices=TYPE_CHOICES, verbose_name="OS Family", default='',
                               help_text="Operating System Family this Operating System is based on", blank=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    version = models.CharField(max_length=16, verbose_name="OS Version")
    release_year = models.PositiveSmallIntegerField(default=datetime.now().year, null=True, blank=True,
                                                    verbose_name="Year of Release",
                                                    help_text="Year the Operating System was released")

    class Meta:
        verbose_name = "Operating System"
        ordering = ['os_type', 'name_short', ]

    def __str__(self):
        return self.name


class CommonIdentifier(models.Model):
    IDENTIFIER_TYPE_CHOICES = getattr(settings, 'HOSTDB_CUSTOM_COMMON_IDENTIFIER_TYPE_CHOICES', (
        ('make', 'Manufacturer'),
        ('model', 'Model'),
        ('gate', 'Gateway IP'),
        ('domain', 'DNS domain')
    ))
    identifier_type = models.CharField(choices=IDENTIFIER_TYPE_CHOICES, max_length=8, verbose_name="Identifier Type")
    identifier = models.CharField(max_length=128)

    class Meta:
        verbose_name = 'Common Identifier'
        unique_together = (('identifier_type', 'identifier',),)

    def __str__(self):
        return "{} : {}".format(self.get_identifier_type_display(), self.identifier)


class CustomSetting(models.Model):
    CUSTOM_SETTING_LIMIT = getattr(settings, 'HOSTDB_CUSTOM_SETTING_LIMIT', (
        models.Q(app_label='hostdb', model='host') |
        models.Q(app_label='hostdb', model='group') |
        models.Q(app_label='bootmgr', model='siteconfig') |
        models.Q(app_label='bootmgr', model='action') |
        models.Q(app_label='bootmgr', model='actionrendertype') |
        models.Q(app_label='bootmgr', model='actioncategory') |
        models.Q(app_label='configstore', model='configtemplate') |
        models.Q(app_label='', model='')
    ))

    name = models.SlugField(max_length=64)
    value = models.CharField(max_length=128)
    description = models.CharField(max_length=128, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, blank=True, null=True,
                                     limit_choices_to=CUSTOM_SETTING_LIMIT,
                                     help_text="Type of Model that this Setting is for.")
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = 'Custom Setting'
        unique_together = ['content_type', 'object_id', 'name']

    def __str__(self):
        return "Custom Setting for {} [ {} : {} ]".format(self.content_object, self.name, self.value)


class Host(models.Model):

    ARCH_CHOICES = getattr(settings, 'HOSTDB_HOST_ARCH_CHOICES', (
        ('none', 'Unknown'),
        ('x86', 'x86'),
        ('x64', 'x64'),
        ('arm', 'ARM'),
    ))
    TYPE_CHOICES = getattr(settings, 'HOSTDB_HOST_TYPE_CHOICES', (
        ('none', 'Unknown'),
        ('vm', 'Virtual Machine'),
        ('bare', 'Bare Metal'),
        ('app', 'Appliance'),
    ))

    name_short = models.SlugField(max_length=32, unique=True, verbose_name="Name", null=True,
                                  help_text="Unique Name to identify this host")
    name = models.CharField(max_length=64, verbose_name="Display Name", default="Unknown")
    description = models.TextField(max_length=512, blank=True, null=True, help_text="Description for this host")
    hostname = models.CharField(max_length=128, blank=True, null=True, verbose_name="FQDN Hostname",
                                help_text="FQDN Hostname this host is known by")
    primary_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="Primary IP Address",
                                              help_text="IP Address this Host can be reached at")
    last_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="Last Known IP Address",
                                           help_text="Last Known IP Address for this Host")
    type = models.CharField(max_length=8, choices=TYPE_CHOICES, blank=True, null=True,
                            verbose_name='Host Type')
    arch = models.CharField(max_length=8, choices=ARCH_CHOICES, blank=True, null=True,
                            verbose_name="System Architecture")
    os = models.ForeignKey(OperatingSystem, blank=True, null=True, verbose_name="Operating System")
    common_identifiers = models.ManyToManyField(CommonIdentifier, blank=True, verbose_name="Common Identifiers",
                                                help_text="Common Identifiers that identify this host and other hosts.")
    custom_settings = GenericRelation(CustomSetting, verbose_name="")
    creation_date = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Creation Date",
                                         help_text="The date and this host has been added.")
    change_date = models.DateTimeField(auto_now=True, null=True, verbose_name="Change Date",
                                       help_text="The date and time this host has been changed last.")

    class Meta:
        verbose_name = "Host"
        ordering = ['name', ]

    def __str__(self):
        return self.name

    def get_custom_setting_filter_objects(self):
        filter_objects = [self, ]
        if self.os:
            filter_objects.append(self.os)
        for group in self.group_set.all():
            filter_objects.append(group)
        for common_identifier in self.common_identifiers.all():
            filter_objects.append(common_identifier)
        return filter_objects

    def get_custom_settings_filter(self):
        from .helpers import get_settings_filter_for_objects
        return get_settings_filter_for_objects(self.get_custom_setting_filter_objects(),)

    def get_custom_settings(self, fallback_objects=None, add_global=True):

        from .helpers import get_settings_filter_for_objects
        filter_objects = self.get_custom_setting_filter_objects()

        if fallback_objects:
            filter_objects = filter_objects + fallback_objects

        setting_filter = get_settings_filter_for_objects(content_objects=filter_objects, add_global=add_global)

        return CustomSetting.objects.filter(setting_filter)

    def get_custom_settings_dict(self, fallback_objects=None, add_global=True):
        from .helpers import get_settings_dict
        return get_settings_dict(
            self.get_custom_settings(fallback_objects=fallback_objects, add_global=add_global)
        )

    @classmethod
    def get_from_unique_identifiers(cls, unique_identifiers):
        from .helpers import get_unique_host_identifiers
        host_identifiers = get_unique_host_identifiers(unique_identifiers)
        host_identifiers_count = host_identifiers.count()

        # throw exception if no host can be found
        if host_identifiers_count < 1:
            raise cls.DoesNotExist

        # if some unique identifiers can not be found, create them for the first found host
        if len(unique_identifiers) > host_identifiers_count:
            print('unknown unique host identifiers found.')

        # no multiple host check required if only one host identifier was found
        if host_identifiers_count == 1:
            return host_identifiers[0].host

        # validate that only one host is associated to all these host identifiers
        for i in range(1,host_identifiers_count-1):
            if host_identifiers[0].host != host_identifiers[i].host:
                raise cls.MultipleObjectsReturned

        return host_identifiers[0].host


class Group(models.Model):
    name = models.SlugField()
    description = models.TextField(max_length=512, blank=True, null=True, help_text="Description for this Group")
    hosts = models.ManyToManyField(Host, blank=True, help_text="Hosts that are Members of this Group")
    common_identifiers = models.ManyToManyField(CommonIdentifier, blank=True, verbose_name="Common Identifiers",
                                                help_text="Common Identifiers associated to this Group")
    custom_settings = GenericRelation(CustomSetting)

    class Meta:
        verbose_name = "Group"
        ordering = ['name', ]

    def __str__(self):
        return self.name


class UniqueHostIdentifier(models.Model):
    IDENTIFIER_TYPE_CHOICES = getattr(settings, 'HOSTDB_CUSTOM_UNIQUE_IDENTIFIER_TYPE_CHOICES', (
        ('uuid', 'Unique Identification Number'),
        ('asset', 'Asset ID'),
        ('serial', 'Serial ID'),
        ('mac', 'MAC Address'),
        ('token', 'Token'),
    ))

    host = models.ForeignKey(Host, help_text="Host to uniquely identify")
    identifier_type = models.CharField(choices=IDENTIFIER_TYPE_CHOICES, max_length=8, verbose_name="Identifier Type",
                                       help_text="Identifier Type to uniquely identify a Host")
    identifier = models.CharField(max_length=128)

    class Meta:
        verbose_name = 'Unique Host Identifier'
        unique_together = (('identifier_type', 'identifier',),)

    def __str__(self):
        return "{} : [ {} - {} ]".format(self.host.name, self.get_identifier_type_display(), self.identifier)
