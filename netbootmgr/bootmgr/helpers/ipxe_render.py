from netbootmgr.bootmgr.helpers import url_builder


def render_boot_script(request, script, host, site_config, settings):
    from netbootmgr.hostdb.helpers import render_template

    context = {'host': host, 'settings': settings, 'request': request, 'site_config': site_config}

    return render_template(template=script, context=context, request=request, recursive=True)


def get_boot_action_script(builder, action):

    script = ""

    if action:
        script = builder.NEWLINE + action.command

    if action.render_type:
        if action.render_type.command_pre:
            script = builder.NEWLINE + action.render_type.command_pre + builder.NEWLINE + script
        if action.render_type.command_post:
            script += builder.NEWLINE + builder.NEWLINE + action.render_type.command_post

    return script


def get_generic_menuentry(builder, section, title, redirect_url, shortcut=None, auto_free=True,
                          replace=False):
    return builder.menu_item(title=title, section=section, key=shortcut), \
           builder.menu_command(section=section,
                                command=builder.redirect(url=redirect_url, auto_free=auto_free, replace=replace),
                                title=title)


def get_menuentry(request, builder, menu_entry, host_id=None, auto_free=True, replace=False):
    section_name = "menu_entry_id_{}".format(menu_entry.id)
    menu_entry_url = url_builder.get_menu_url(request=request, menuentry_id=menu_entry.id, host_id=host_id)
    return get_generic_menuentry(builder=builder, section=section_name, title=menu_entry.name(),
                                 shortcut=menu_entry.shortcut, redirect_url=menu_entry_url,
                                 auto_free=auto_free, replace=replace)


def get_action_menuentry(request, builder, action, section=None, title=None, host_id=None):
    if section is None:
        section = "menu_action_id_{}".format(action.id)
    if title is None:
        title = action.name

    action_url = url_builder.get_action_url(request=request, action_id=action.id, host_id=host_id)
    return get_generic_menuentry(builder=builder, section=section, title=title,
                                 redirect_url=action_url, auto_free=True, replace=False)


def get_menu_menuentry(request, builder, menu, section=None, title=None, host_id=None):
    if section is None:
        section = "menu_id_{}".format(menu.id)
    if title is None:
        title = menu.name

    action_url = url_builder.get_menu_url(request=request, menu_id=menu.id, host_id=host_id)
    return get_generic_menuentry(builder=builder, section=section, title=title,
                                 redirect_url=action_url, auto_free=True, replace=True)


def get_boot_menu_script(request, builder, menu, host_id=None, back_menu=None, fallback_action=None, auto_reload=False,
                         show_reconnect=False, timeout_s=10, reload_delay_s=10, reconnect_delay_s=10):

    if reload_delay_s > 0:
        reload_delay_s = str(reload_delay_s)
    else:
        reload_delay_s = '11'

    if reconnect_delay_s > 0:
        reconnect_delay_s = str(reconnect_delay_s)
    else:
        reconnect_delay_s = '11'

    menus_count = 0
    actions_count = 0
    script_header = ''
    script_footer = ''
    menu_header = ''
    menu_footer = ''
    menus_items = ''
    action_items = ''
    command_sections = ''
    menu_default = 'menu_reload'

    # skip error handling sections
    script_header += builder.goto('menu_start')

    # end delay section
    script_header += builder.jump_point('end_delay')
    script_header += builder.if_then(
        builder.echo(message='Exit in {} seconds. Press Ctrl+C to Reconnect.'.format(reconnect_delay_s)),
        builder.if_not(builder.sleep(seconds=reconnect_delay_s, newline=False),
                       builder.goto(section='reconnect', newline=False))
    )
    script_header += builder.goto('menu_end')

    # reconnect delay section
    script_header += builder.jump_point('reconnect_delay')
    script_header += builder.if_then(
        builder.echo(message='Reconnecting in {} seconds. Press Ctrl+C to End.'.format(reconnect_delay_s)),
        builder.if_not(builder.sleep(seconds=reconnect_delay_s, newline=False),
                       builder.goto(section='menu_end', newline=False))
    )

    # reconnect section
    script_header += builder.jump_point('reconnect')
    script_header += builder.redirect(url=url_builder.get_connect_url(request=request, host_id=host_id),
                                      auto_free=True, replace=True)

    # reload delay section
    script_header += builder.jump_point('menu_reload')
    script_header += builder.if_then(
        builder.echo('Reloading menu in {} seconds. Press Ctrl+C to End.'.format(reload_delay_s)),
        builder.if_not(builder.sleep(seconds=reload_delay_s, newline=False),
                       builder.goto(section='menu_end', newline=False))
    )
    script_header += builder.goto('menu_start')

    # create action_unfinished section
    script_header += builder.jump_point('action_unfinished')
    if auto_reload:
        script_header +=  builder.if_then(builder.echo('Action not terminated. Reloading Menu.'),
                                          builder.goto('menu_reload', newline=False))
    else:
        script_header += builder.if_then(builder.echo('Action finished. Continuing with Boot.'),
                                         builder.goto('end_delay', newline=False))

    # create action_failed section
    script_header += builder.jump_point('action_failed')
    script_header += builder.if_then(builder.echo('Failed to launch selected boot command.'),
                                     builder.goto('menu_reload', newline=False))
    # create menu_failed section
    script_header += builder.jump_point('menu_failed')
    script_header += builder.if_then(builder.echo('Failed to select entry from menu.'),
                                     builder.goto('menu_reload', newline=False))

    # create menu header and jump point
    menu_header += builder.jump_point("menu_start")
    menu_header += builder.menu_header(title=menu.name)

    # create menu entries for sub menus and actions store and them in different categories
    for menu_entry in menu.menuentry_set.all():
        if menu_entry.content_type.name == 'Boot Menu':
            menu_item, menu_command = get_menuentry(request=request, builder=builder, menu_entry=menu_entry,
                                                    host_id=host_id, auto_free=True, replace=True)
            menus_items += menu_item
            command_sections += builder.if_not(menu_command, builder.goto(section='menu_failed', newline=False))
            command_sections += builder.goto('menu_reload')
            menus_count += 1
        else:
            menu_item, menu_command = get_menuentry(request=request, builder=builder, menu_entry=menu_entry,
                                                    host_id=host_id, auto_free=True, replace=False)
            action_items += menu_item
            command_sections += builder.if_not(menu_command, builder.goto(section='action_failed', newline=False))
            command_sections += builder.goto('action_unfinished')
            actions_count += 1

    # add menu gap for sub menus
    if menus_count == 1:
        menus_items = builder.menu_gap(title='Boot Menu:') + menus_items
    elif menus_count > 1:
        menus_items = builder.menu_gap(title='Boot Menus ({})'.format(menus_count)) + menus_items
    else:
        menus_items = builder.menu_gap(title='No Boot Menus.')

    # add menu gap for actions
    if actions_count == 1:
        action_items = builder.menu_gap(title='Boot Action:') + action_items
    elif actions_count > 1:
        action_items = builder.menu_gap(title='Boot Actions ({})'.format(actions_count)) + action_items
    else:
        action_items = builder.menu_gap(title='No Boot Actions.')

    if actions_count + menus_count == 0:
        action_items = ''
        menus_items = builder.menu_gap(title='Boot Menu is empty.')

    # create default menu header and entry
    menu_footer += builder.menu_gap(title='Default:')

    # only create back_to_menu entry if there is a menu to go back to
    if back_menu and back_menu.id != menu.id:
        menu_back_entry_item, menu_back_entry_command = \
            get_menu_menuentry(request=request, builder=builder, menu=back_menu, section='fallback_menu',
                               title='Back to {}'.format(back_menu.name), host_id=host_id)
        menu_default = 'fallback_menu'
        menu_footer += menu_back_entry_item
        command_sections += builder.if_not(menu_back_entry_command,
                                           builder.goto(section='action_failed', newline=False))
        command_sections += builder.goto('menu_reload')

    # create reconnect entry if enabled
    if show_reconnect:
        menu_footer += builder.menu_item(title='Reload from Server.', section='reconnect')

    # create fallback_action if set
    if fallback_action:
        fallback_entry_item, fallback_entry_command = \
            get_action_menuentry(request, builder, action=fallback_action, section='fallback_action', host_id=host_id)
        menu_footer += fallback_entry_item
        command_sections += builder.if_not(fallback_entry_command,
                                           builder.goto(section='action_failed', newline=False))
        command_sections += builder.goto('action_unfinished')

        # override default menu entry if unchanged
        if menu_default == 'menu_reload':
            menu_default = 'fallback_action'
    # set fallback_action to menu_end otherwise
    else:
        menu_footer += builder.menu_item(title='Exit iPXE and continue with boot.', section='menu_end')
        if menu_default == 'menu_reload':
            menu_default = 'menu_end'

    # create choose command and goto menu_canceled section if the menu is canceled
    menu_footer += builder.if_not(
        builder.menu_choose(setting='menu_choose', timeout_ms=timeout_s * 1000, default=menu_default),
        builder.goto('menu_failed', newline=False)
    )
    menu_footer += builder.goto(builder.get_setting('menu_choose'))

    script_footer += builder.NEWLINE
    script_footer += builder.jump_point(section='menu_end')
    script_footer += builder.get_exit()

    # compile the script and return it
    return script_header + \
        builder.NEWLINE + \
        menu_header + \
        menus_items + \
        action_items + \
        menu_footer + \
        builder.NEWLINE + \
        command_sections + \
        script_footer

