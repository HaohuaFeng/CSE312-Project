FROM python:3.8

ENV HOME /root
WORKDIR /root



COPY . .
RUN pip install -r requirement.txt


EXPOSE 8000

CMD python3 server.py