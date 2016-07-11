from netbootmgr.hostdb.models import *
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.conf import settings


# region Generic Inlines


class CustomSettingsGenericInline(GenericTabularInline):
    model = CustomSetting
    ordering = ['name']
    extra = 0


# endregion
# region Regular Inlines


class UniqueHostIdentifierInline(admin.TabularInline):
    model = UniqueHostIdentifier
    fields = ('identifier_type', 'identifier',)
    extra = 0


class HostGroupInline(admin.TabularInline):
    Group.hosts.through.__str__ = lambda x: 'Group Membership'
    model = Group.hosts.through
    extra = 0
    verbose_name = "Host Group Membership"


# endregion
# region Admin Models


@admin.register(CommonIdentifier)
class CommonIdentifierAdminModel(admin.ModelAdmin):
    list_display = ('identifier_type', 'identifier', )
    search_fields = ('identifier_type', 'identifier', )
    list_filter = ['identifier_type', ]


@admin.register(UniqueHostIdentifier)
class UniqueIdentifierAdminModel(admin.ModelAdmin):
    list_display = ('host', 'identifier_type', 'identifier', )
    search_fields = ('identifier', )
    list_filter = ['identifier_type','host', ]


@admin.register(CustomSetting)
class CustomSettingAdminModel(admin.ModelAdmin):
    list_display = ('name', 'value', 'description', 'content_type', 'content_object', )
    search_fields = ('name', 'value', 'description', )
    list_filter = ['name', 'content_type', ]
    related_lookup_fields = {'generic': [['content_type', 'object_id'], ], }


@admin.register(Host)
class HostAdminModel(admin.ModelAdmin):
    list_display = ('name', 'hostname', 'type', 'arch', 'os', 'primary_ip', 'last_ip',
                    'name_short', 'description', 'creation_date', 'change_date', )
    search_fields = ('name', 'name_short', 'hostname', 'description', 'primary_ip', 'last_ip')
    list_filter = ['type', 'arch', 'os', 'creation_date', 'change_date', ]
    inlines = [
        UniqueHostIdentifierInline,
        CustomSettingsGenericInline,
        HostGroupInline,
    ]

    filter_horizontal = ['common_identifiers']

    if 'bootmgr' in settings.INSTALLED_APPS:
        from netbootmgr.bootmgr.admin import FallbackActionGenericInline, HostTaskTabInline
        inlines.append(HostTaskTabInline)
        inlines.append(FallbackActionGenericInline)


@admin.register(Group)
class GroupAdminModel(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    inlines = [
        CustomSettingsGenericInline,
    ]


@admin.register(OperatingSystem)
class OperatingSystemAdminModel(admin.ModelAdmin):
    list_display = ('name', 'description', 'name_short', 'version', 'os_type', )


# endregion
