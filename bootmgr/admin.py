from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from netbootmgr.hostdb.admin import CustomSettingsGenericInline
from .models import *


# region Generic Inlines


class FallbackActionGenericInline(GenericTabularInline):
    model = FallbackAction
    extra = 0
    max_num = 1


class MenuEntryGenericInline(GenericTabularInline):
    model = MenuEntry
    ordering = ['order', ]
    extra = 0
    verbose_name = "Parent Menu"
    verbose_name_plural = "Parent Menus"
    sortable_field_name = "order"


# endregion
# region Regular Inlines


class FallbackActionTabInline(admin.TabularInline):
    model = FallbackAction
    extra = 0
    verbose_name = "Fallback Boot Action"
    verbose_name_plural = "Fallback Boot Actions"

    related_lookup_fields = {
        'generic': [['content_type', 'object_id'], ],
    }


class HostTaskTabInline(admin.TabularInline):
    model = HostTask
    ordering = ['order', ]
    extra = 0
    sortable_field_name = "order"
    verbose_name = "Boot Task"
    verbose_name_plural = "Boot Tasks"


class SiteConfigTabInline(admin.TabularInline):
    model = SiteConfig
    extra = 1
    max_num = 1


class MenuEntryTabInline(admin.TabularInline):
    model = MenuEntry
    ordering = ['order', ]
    extra = 0
    sortable_field_name = "order"
    related_lookup_fields = {
        'generic': [['content_type', 'object_id'], ],
    }


# endregion
# region Admin Models


@admin.register(MenuEntry)
class MenuEntryAdmin(admin.ModelAdmin):
    list_display = ('name', 'content_type','menu', 'shortcut', 'order', )
    list_filter = ['menu', 'content_type', ]


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    inlines = [MenuEntryTabInline, MenuEntryGenericInline, ]
    list_display = ('name', 'description', )
    search_fields = ('name', 'description', )


@admin.register(ActionRenderType)
class ActionRenderTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', )
    search_fields = ('name', 'description')


@admin.register(ActionCategory)
class ActionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', )
    search_fields = ('name', 'description')


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    inlines = [CustomSettingsGenericInline, HostTaskTabInline, FallbackActionTabInline, MenuEntryGenericInline, ]
    list_display = ('name', 'action_category', 'render_type', 'description', 'change_date', 'creation_date', )
    search_fields = ('name', 'description')
    list_filter = ['action_category', 'render_type', 'change_date', 'creation_date', ]


@admin.register(FallbackAction)
class FallbackActionAdmin(admin.ModelAdmin):
    list_display = ('action', 'content_type', )
    search_fields = ('action', 'content_type', )
    list_filter = ['action', 'content_type', ]

    related_lookup_fields = {
        'generic': [['content_type', 'object_id'], ],
    }


@admin.register(HostTask)
class HostTaskAdmin(admin.ModelAdmin):
    list_display = ('host', 'action', )
    search_fields = ('host', 'action', )
    list_filter = ['host', 'action', ]


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ('url', 'description', 'menu', 'menu_timeout', 'timeout_action', 'is_secure')
    search_fields = ('url', 'description', )
    list_filter = ['menu', 'menu', 'menu_timeout', 'timeout_action']


# endregion
