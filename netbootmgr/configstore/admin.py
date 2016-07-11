from django.contrib import admin
from netbootmgr.hostdb.admin import CustomSettingsGenericInline
from netbootmgr.configstore.models import *


@admin.register(ConfigTemplate)
class ConfigurationTemplateAdminModel(admin.ModelAdmin):
    list_display = ('name', 'description', 'mime_type', 'change_date', 'creation_date', )
    search_fields = ('name', 'description')
    list_filter = ['mime_type', 'change_date', 'creation_date', ]
    inlines = [CustomSettingsGenericInline, ]
