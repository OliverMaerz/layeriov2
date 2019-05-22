FROM python:3.7

COPY ./app /app
COPY ./requirements.txt /config/
COPY ./docker_mysql.sql /config/

RUN pip install -r /config/requirements.txt
# RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get update
# RUN apt-get -q -y install mysql-server
RUN apt-get install -y software-properties-common dirmngr
RUN apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 0xF1656F24C74CD1D8
RUN add-apt-repository 'deb [arch=amd64,i386,ppc64el] http://mirror.zol.co.zw/mariadb/repo/10.3/debian stretch main'
RUN apt-get update
RUN ["/bin/bash", "-c", "debconf-set-selections <<< 'mariadb-server-10.3 mysql-server/root_password password rootpass'"]
RUN ["/bin/bash", "-c", "debconf-set-selections <<< 'mariadb-server-10.3 mysql-server/root_password_again password rootpass'"]
RUN apt-get -y install mariadb-server-10.3
RUN service mysql start && mysql -u root -prootpass < /config/docker_mysql.sql
EXPOSE 80
CMD service mysql start && uvicorn app.main:app --host 0.0.0.0 --port 80

