FROM python:3
RUN groupadd -g 9000 exabgp && \
    useradd -u 9000 -g 9000 -d /tmp exabgp
RUN git clone https://github.com/Exa-Networks/exabgp/ && cd exabgp/ && git checkout tags/4.2.20
RUN cd exabgp && pip install .
RUN pip install requests
COPY entrypoint.sh /entrypoint.sh
COPY healthcheck.py /healthcheck.py
RUN mkfifo /run/exabgp.in && \
    mkfifo /run/exabgp.out && \
    chown exabgp:exabgp /run/exabgp.in && \
    chown exabgp:exabgp /run/exabgp.out && \
    chmod 600 /run/exabgp.in && \
    chmod 600 /run/exabgp.out
ENV PYTHONUNBUFFERED=1
ENV PYTHONWARNINGS="ignore:Unverified HTTPS request"
USER exabgp
CMD [ "exabgp" ]
ENTRYPOINT [ "/entrypoint.sh" ]
