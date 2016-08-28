FROM django:latest
MAINTAINER Dominic S. "docker@dominic86.de"

RUN pip install django-jenkins coverage pep8 pyflakes

RUN wget -O - https://git.dominic86.de/netbootmgr/django_netbootmgr/archive/master.tar.gz | tar xzf - django_netbootmgr/netbootmgr && \
	mv django_netbootmgr/netbootmgr netbootmgr && \
	mkdir -p /app/data && \
	mkdir -p /app/src && \
	mkdir -p /app/django_netbootmgr && \
	mkdir -p /app/reports

COPY django-template /app/src/django_template

COPY init.sh /app/init

RUN useradd -M -u 1000 -d /app django && \
	django-admin startproject --template=/app/src/django_template bootmgr /app && \
	chown django:django /app -R && \
	chmod 500 /app/init

WORKDIR /app

VOLUME ["/app/reports"]

CMD ["/app/init"]