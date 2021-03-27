FROM python:3.8

ENV HOME /root
WORKDIR /root

COPY . .
RUN pip install -r requirement.txt

EXPOSE 8000
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.8.0/wait /wait
RUN chmod +x /wait
CMD /wait && python3 server.py