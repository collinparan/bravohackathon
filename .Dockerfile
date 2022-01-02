FROM centos:8
ENV container docker
RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == \
systemd-tmpfiles-setup.service ] || rm -f $i; done); \
rm -f /lib/systemd/system/multi-user.target.wants/*;\
rm -f /etc/systemd/system/*.wants/*;\
rm -f /lib/systemd/system/local-fs.target.wants/*; \
rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -f /lib/systemd/system/basic.target.wants/*;\
rm -f /lib/systemd/system/anaconda.target.wants/*;
VOLUME [ "/sys/fs/cgroup" ]
CMD ["/usr/sbin/init"]

RUN yum install python3 -y && \
ln -fs /usr/bin/python3 /usr/bin/python && \
ln -fs /usr/bin/pip3 /usr/bin/pip

RUN yum install ncurses

COPY ./ ./
RUN pip install -r requirements.txt
# RUN chmod u+x setup.sh
# RUN ./setup.sh 

EXPOSE 80 8080 8443