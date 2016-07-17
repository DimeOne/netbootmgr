from django.apps import AppConfig

default_app_config = 'netbootmgr.NetBootMgrAppConfig'

class NetBootMgrAppConfig(AppConfig):
    name = 'netbootmgr'
    label = 'netbootmgr'
    verbose_name = "Network Boot Manager"
