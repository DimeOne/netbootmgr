from django.conf import settings
from django.apps import AppConfig

MIME_TYPE_CHOICES = getattr(settings, 'MIME_TYPE_CHOICES', (
    ('text/plain', 'plain text'),
    ('text/html', 'html'),
    ('text/javascript', 'javascript'),
    ('text/css', 'css'),
    ('text/xml', 'xml (text)'),
    ('application/xml', 'xml (application)'),
    ('application/json', 'json'),
    ('text/comma-separated-values', 'csv'),
    ('application/x-sh', 'shell script'),
))


class ConfigStoreAppConfig(AppConfig):
    name = 'netbootmgr.configstore'
    verbose_name = "Configuration Store"

