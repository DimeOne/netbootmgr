from django.db import models

from .settings import MIME_TYPE_CHOICES


class ConfigTemplate(models.Model):
    name = models.SlugField(unique=True, help_text="Unique Name without blanks")
    description = models.CharField(max_length=128, blank=True, null=True,
                                   help_text="Text describing this Configuration Template")
    mime_type = models.CharField("MIME Type", max_length=16, help_text="MIME Type of the template",
                                 choices=MIME_TYPE_CHOICES)
    template = models.TextField(help_text="Template to generate the Configuration from")
    creation_date = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Creation Date",
                                         help_text="The date when madded.")
    change_date = models.DateTimeField(auto_now=True, null=True, verbose_name="Change Date",
                                       help_text="Last change date.")

    class Meta:
        verbose_name = "Configuration Template"

    def __str__(self):
        return self.name

    def render_for_host(self, host, site_config=None, request=None):
        from netbootmgr.hostdb.helpers import render_host_template
        return render_host_template(host=host, template=self.template, site_config=site_config, request=request,
                                    fallback_objects=[self])
