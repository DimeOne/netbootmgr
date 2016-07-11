=====
Net Boot Manager
=====


Net Boot Manager is a simple Django app to manage Network Boot Environments.

Quick start
-----------

1. Add "netbootmgr.hostdb","netbootmgr.configstore","netbootmgr.bootmgr" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'netbootmgr.hostdb',
        'netbootmgr.configstore',
        'netbootmgr.bootmgr',
    ]

2. Include the polls URLconf in your project urls.py like this::

    url(r'^admin/', admin.site.urls),
    url(r'^boot/', include('netbootmgr.bootmgr.urls')),
    url(r'^hostdb/', include('netbootmgr.hostdb.urls')),
    url(r'^configstore/', include('netbootmgr.configstore.urls')),

3. Run `python manage.py migrate` to create the models.

4. Run `python manage.py createsuperuser` to create an administrative user.

5. Run `python manage.py runserver 0.0.0.0:8000` to start the development server 

6. Visit http://127.0.0.1:8000/admin/ to configure your boot environment.