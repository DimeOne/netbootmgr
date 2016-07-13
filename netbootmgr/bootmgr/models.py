from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from netbootmgr.hostdb.models import Host
from .helpers.settings import AUTO_CREATE_NEW_SITES, BOOT_MENU_SHORTCUT_CHOICES


class ActionRenderType(models.Model):
    name = models.CharField(max_length=64, )
    description = models.CharField(max_length=128, blank=True, null=True,
                                   help_text='Description for this Boot Action Type.')
    command_pre = models.TextField(verbose_name="Pre Action Command", blank=True, null=True,
                                   help_text='Commands to render before Action command.')
    command_post = models.TextField(verbose_name="Post Action Command", blank=True, null=True,
                                    help_text='Commands to render after Action command.')

    class Meta:
        verbose_name = "Boot Action Render Type"
        ordering = ['name', ]

    def __str__(self):
        return self.name


class ActionCategory(models.Model):
    name = models.CharField(max_length=64, )
    description = models.CharField(max_length=128, blank=True, null=True,
                                   help_text='Description for this Boot Action Type.')

    class Meta:
        verbose_name = "Boot Action Category"
        ordering = ['name', ]

    def __str__(self):
        return self.name


class Action(models.Model):
    name = models.CharField(max_length=64, )
    description = models.CharField(max_length=128, blank=True, null=True,
                                   help_text='Description for this Boot Action.')
    render_type = models.ForeignKey(ActionRenderType, verbose_name="Template Render Type", blank=True, null=True,
                                    help_text="The Action Render Type determines how the Script is rendered")
    action_category = models.ForeignKey(ActionCategory, verbose_name="Category", blank=True, null=True,
                                        help_text="Category helps to filter by.")
    command = models.TextField(help_text='Boot Command to render as template.')
    creation_date = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Creation Date",
                                         help_text="The date and this Boot Command has been added.")
    change_date = models.DateTimeField(auto_now=True, null=True, verbose_name="Change Date",
                                       help_text="The date and time this Boot Command has been changed last.")

    class Meta:
        verbose_name = "Boot Action Template"
        ordering = ['name', ]

    def __str__(self):
        return self.name


class Menu(models.Model):
    name = models.CharField(max_length=64, )
    description = models.CharField(max_length=128, blank=True, null=True,
                                   help_text='Description for this Boot Menu.')

    class Meta:
        verbose_name = "Boot Menu"
        ordering = ['name', ]

    def __str__(self):
        return self.name


class MenuEntry(models.Model):
    MENU_ENTRY_LIMIT = getattr(settings, 'BOOTMGR_BOOT_MENU_ENTRY_LIMIT', (
        models.Q(app_label='bootmgr', model='menu') | models.Q(app_label='bootmgr', model='action')
    ))

    menu = models.ForeignKey(Menu, null=True, blank=True, verbose_name="Parent Menu")
    shortcut = models.CharField(max_length=6, blank=True, null=True, choices=BOOT_MENU_SHORTCUT_CHOICES,
                                verbose_name="Shortcut Key")
    order = models.SmallIntegerField(blank=True, null=True)
    content_type = models.ForeignKey(ContentType, limit_choices_to=MENU_ENTRY_LIMIT, verbose_name="Entry Type")
    object_id = models.PositiveIntegerField(verbose_name="Entry ID")
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "Boot Menu Entry"
        verbose_name_plural = "Boot Menu Entries"
        ordering = ['content_type','order', ]

    def __str__(self):
        if self.content_object:
            return self.content_object.name
        return "Boot Menu Entry #{0}".format(self.id)

    def name(self):
        if self.content_object:
            return "{} / {}".format(self.menu.name, self.content_object.name)
        return ""


class HostTask(models.Model):
    host = models.ForeignKey(Host, help_text="Host that should execute the Boot Action.")
    action = models.ForeignKey(Action, verbose_name="Boot Action",
                               help_text="Boot Action that should be executed by the Host.")
    order = models.PositiveIntegerField(blank=True, null=True, verbose_name="Priority",
                                        help_text="Used to determine Task execution priority.")

    class Meta:
        verbose_name = "Host Boot Task"
        ordering = ['host', 'order', ]

    def __str__(self):
        return "Host Boot Task #{0}".format(self.id)


class FallbackAction(models.Model):
    FALLBACK_LIMIT = getattr(settings, 'BOOTMGR_BOOT_FALLBACK_LIMIT', (
        models.Q(app_label='hostdb', model='host') | models.Q(app_label='hostdb', model='group') |
        models.Q(app_label='bootmgr', model='siteconfig')
    ))

    action = models.ForeignKey(Action, verbose_name="Fallback Boot Action",
                               help_text="Boot Action that should be executed by the Host if no task exist")
    content_type = models.ForeignKey(ContentType, null=True, blank=True, limit_choices_to=FALLBACK_LIMIT,
                                     verbose_name="Entry Type")
    object_id = models.PositiveIntegerField(verbose_name="Entry ID")
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "Boot Fallback Action"
        unique_together = ('content_type', 'object_id')

    def __str__(self):
        return "Boot Command Fallback #{0}".format(self.id)


class SiteConfig(models.Model):
    url = models.URLField(verbose_name="Site URL", unique=True)
    name = models.CharField(max_length=64, blank=True, null=True)
    description = models.CharField(
        verbose_name='Site Description',
        max_length=128,
        blank=True,
        null=True,
        help_text='Description for this Boot Site Config.'
    )
    menu = models.ForeignKey(
        Menu,
        verbose_name="Default Boot Menu",
        blank=True,
        null=True,
        help_text="The Default Boot Menu to show for this Site"
    )
    reload_delay = models.PositiveSmallIntegerField(
        verbose_name='Reload delay in Seconds',
        default=10,
        help_text='Time to wait before reloading the menu after an action has finished without termination.'
    )
    reconnect_delay = models.PositiveSmallIntegerField(
        verbose_name='Reconnect delay in Seconds',
        default=15,
        help_text='Time to wait before reconnecting if required.'
    )
    menu_timeout = models.PositiveSmallIntegerField(
        verbose_name='Timeout in Seconds',
        default=30,
        help_text='Time to wait before choosing the default menu item. 0=never.'
    )
    timeout_action = models.ForeignKey(
        Action,
        verbose_name='Default Timeout Action',
        blank=True,
        null=True,
        help_text="Action that will be executed if Host has no Fallback Action."
    )
    initial_host_action = models.ForeignKey(
        Action,
        related_name='initial_host_task',
        verbose_name='Initial Host Action Task',
        blank=True,
        null=True,
        help_text="Action that will be set as Task for Hosts connecting for the first time."
    )
    auto_create_hosts = models.BooleanField(
        verbose_name='Auto Create New Hosts',
        default=True,
        help_text='Automatically create entries for unknown hosts connecting to this site.'
    )
    show_menu_fallback = models.BooleanField(
        verbose_name='Show Menu before Fallback',
        default=True,
        help_text='Show menu before booting fallback entry if existing.'
    )
    show_reconnect = models.BooleanField(
        verbose_name='Show Reconnect',
        default=True,
        help_text='Show reconnect action within defaults in menus.'
    )
    auto_reload = models.BooleanField(
        verbose_name='Auto Reload Menu',
        default=False,
        help_text='Reload Menu if selected Action has returned successfully. Otherwise exit to BIOS / UEFI.'
    )

    def is_secure(self):
        return self.url.lower().startswith('https://')

    is_secure.boolean = True

    @classmethod
    def get_from_request(cls, request):
        from netbootmgr.bootmgr.helpers.url_builder import get_root_url
        root_url = get_root_url(request)
        return cls.objects.get(url=root_url)

    @classmethod
    def get_or_create_from_request(cls, request, create_new_sites=AUTO_CREATE_NEW_SITES):
        from netbootmgr.bootmgr.helpers.url_builder import get_root_url
        root_url = get_root_url(request)
        created = False

        if create_new_sites:
            site_config, created = cls.objects.get_or_create(url=root_url)
        else:
            site_config = cls.objects.get(url=root_url)

        return site_config, created

    class Meta:
        verbose_name = "Boot Site Config"

    def __str__(self):
        return "Boot Site Config #{0}".format(self.id)
