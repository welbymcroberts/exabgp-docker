FROM python:3
RUN git clone https://github.com/Exa-Networks/exabgp/ && cd exabgp/ && git checkout tags/4.2.11
RUN cd exabgp && pip install .
CMD [ "exabgp", "--help" ]
