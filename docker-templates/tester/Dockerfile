FROM django:1.10-python3
MAINTAINER Dominic S. "docker@dominic86.de"

RUN apt-get update && \
	apt-get install wget -y && \
	rm -rf /var/lib/apt/lists/* && \
	pip install django-jenkins coverage pep8 pyflakes pylint

WORKDIR /app

RUN wget -q -O - https://git.dominic86.de/netbootmgr/netbootmgr/archive/master.tar.gz | tar xzf - netbootmgr/netbootmgr --strip-components=1 && \
	mkdir -p /app/data && \
	mkdir -p /app/src && \
	mkdir -p /app/reports

COPY django-template /app/src/django_template

COPY init.sh /app/init

RUN useradd -M -u 1000 -d /app django && \
	django-admin startproject --template=/app/src/django_template bootmgr /app && \
	chown django:django /app -R && \
	chmod 500 /app/init


VOLUME ["/app/reports"]

CMD ["/app/init"]