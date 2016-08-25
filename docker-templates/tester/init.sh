#!/bin/bash

set -e

function echo_title () {
	echo =================================================================================
	echo === $*
	echo =================================================================================
}

if [ ! -f /app/bootmgr/settings.py ]; then
	echo_title No settings.py found. Generating new django project configuration files from template.
	django-admin startproject --template=/app/src/django_template bootmgr /app
fi

echo_title starting tests
exec python manage.py jenkins netbootmgr
