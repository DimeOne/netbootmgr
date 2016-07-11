from django.core.validators import RegexValidator
from django.conf import settings
from django.apps import AppConfig

MAX_RECURSION_LEVEL = getattr(settings, 'HOSTDB_RENDER_MAX_RECURSION_LEVEL', 10)

MAC_ADDRESS_VALIDATOR = getattr(settings,
                                'HOSTDB_MAC_ADDRESS_VALIDATOR',
                                RegexValidator(r'^([0-9a-fA-F]{2}([:-]?|$)){6}$',
                                               'Only valid mac address with : or - as delimiter allowed',
                                               'Invalid mac address', ))


class HostDBAppConfig(AppConfig):
    name = 'netbootmgr.hostdb'
    label = 'hostdb'
    verbose_name = "Host Database"

