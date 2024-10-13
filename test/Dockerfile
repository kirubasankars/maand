FROM maand

RUN pip install docker
COPY scripts /scripts
RUN chmod +x /scripts/*.sh

ENTRYPOINT ["tini", "-g", "--", "/scripts/start.sh"]