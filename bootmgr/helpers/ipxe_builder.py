NAME = 'ipxe'

NEWLINE = "\r\n"


def get_header():
    """ return ipxe header which is required for an ipxe script to be interpreted as such """
    return '#!ipxe' + NEWLINE


def echo(message, newline=True):
    """ returns an echo command with given message """
    return get_newline(newline) + "echo " + message


def sleep(seconds, newline=True):
    """ returns a sleep command with given seconds as timeout """
    return get_newline(newline) + "sleep " + seconds


def redirect(url, auto_free=False, replace=False, newline=True):
    """ returns an chain command to chain load an other ipxe script """
    ipxe_replace = "--replace " if replace else ""
    ipxe_auto_free = "--autofree " if auto_free else ""
    return get_newline(newline) + "chain " + ipxe_auto_free + ipxe_replace + url


def redirect_safe(url, auto_free=True, replace=False, newline=True):
    """ returns a redirect command encapsulated in if_not which will ignore a failed request
        use this function rather than redirect if you expect a http request with empty result
        some requests won't contain any ipxe scripts and will fail, so we need to catch it by calling it with
        an if_not - in ipxe this  means that a || will be suffixed following the empty command. Because of
        that uncertainty of the of the success we don't want that script to replace the old one by default """
    return if_not(redirect(url, auto_free, replace, newline), "")


def redirect_goto(url, section, auto_free=True, replace=False, newline=True):
        """ jumps to section if redirect failed """
        return if_not(redirect(url, auto_free, replace, newline), goto(section=section, newline=False), newline=False)


def get_exit(newline=True):
    """ returns an exit command for an ipxe script """
    return get_newline(newline) + "exit"


def get_reboot(newline=True):
    """ returns an exit command for an ipxe script """
    return get_newline(newline) + "reboot"


def jump_point(section):
    """ returns a jump point which can ge targeted with goto or other means - will always have a newline"""
    return NEWLINE + ':' + section


def goto(section, newline=True):
    """ returns a command to jump to an existing jump point """
    return get_newline(newline) + "goto " + section


def menu_header(title, newline=True):
    """ returns the command to start a menu in an ipxe script """
    return get_newline(newline) + "menu " + title


def menu_item(title, section, key=None, newline=True):
    """ returns the command for a menu item in an ipxe menu """
    from netbootmgr.bootmgr.helpers.settings import BOOT_MENU_SHORTCUT_CHOICES_DICT
    ipxe_menu_key = ''
    if key:
        ipxe_menu_key = " --key {}".format(key) if key else ""
        title = get_edge_titles(title, "[{}]".format(BOOT_MENU_SHORTCUT_CHOICES_DICT[key]))
    else:
        title = get_filled_title(title)

    return get_newline(newline) + "item{} {} {}".format(ipxe_menu_key, section, title)


def menu_gap(title, newline=True):
    """ returns the command for a menu gap in an ipxe menu """
    return get_newline(newline) + "item --gap -- " + get_centered_title(title)


def menu_command(section, command, title=None):
    """ returns the command required for a menu item to work, these are the jump points where the ipxe client
        jumps to when calling a menu entry """
    if title:
        return jump_point(section) + echo('Booting "{}"'.format(title)) + command
    return jump_point(section) + command


def menu_choose(setting, timeout_ms=None, default=None, newline=True):
    """ returns the command for selecting in an ipxe menu, define timeout and default action on timeout if you want """
    menu_default = "--default {} ".format(default) if default else ""
    menu_timeout = "--timeout {} ".format(str(timeout_ms)) if timeout_ms else ""
    return get_newline(newline) + "choose " + menu_default + menu_timeout + setting


def if_isset(var_name, action, newline=True):
    """ returns the commands to execute the given action if the var_name is set in an ipxe script """
    return get_newline(newline) + if_then(isset(var_name), action)


def if_not_isset(var_name, action, newline=True):
    """ returns the commands to execute the given action if the var_name is not set in an ipxe script """
    return get_newline(newline) + if_not(isset(var_name), action)


def isset(var_name, newline=False):
    """ returns the command to test if a variable is set """
    return get_newline(newline) + "isset " + var_name


def if_then(condition, action, newline=False):
    """ returns commands to execute the given action then the given condition is true in an ipxe script """
    return get_newline(newline) + condition + " && " + action


def if_not(condition, action, newline=False):
    """ returns the command for an action if condition is true """
    return get_newline(newline) + condition + " || " + action


def get_centered_title(title):
    """ returns a string which is centered to a window width specified in settings.py or settings_override.py """
    from netbootmgr.bootmgr.helpers.settings import MAX_IPXE_WINDOW_WIDTH
    return " {} ".format(title.strip()).center(MAX_IPXE_WINDOW_WIDTH, '=')


def get_edge_titles(left, right):
    from netbootmgr.bootmgr.helpers.settings import MAX_IPXE_WINDOW_WIDTH
    space_to_fill = MAX_IPXE_WINDOW_WIDTH - len(left + right) - 1
    filler = ""
    if space_to_fill > 0:
        if space_to_fill % 2 > 0:
            space_to_fill -= 1
            filler = "."
        space_to_fill = int(space_to_fill / 2)

        return left + " " + ". " * space_to_fill + "" + filler + right

    return left + right


def get_filled_title(title):
    from netbootmgr.bootmgr.helpers.settings import MAX_IPXE_WINDOW_WIDTH
    space_to_fill = MAX_IPXE_WINDOW_WIDTH - len(title) - 1
    if space_to_fill > 0:
        if space_to_fill % 2 > 0:
            space_to_fill += 1
        space_to_fill = int(space_to_fill / 2)
    return title + " " + ". " * space_to_fill


def get_newline(newline=True):
    """ returns a newline for ipxe scripts if newline is true """
    return NEWLINE if newline else ""


def get_setting(setting):
    """ returns a representation of the setting a value """
    return "${" + setting + "}"