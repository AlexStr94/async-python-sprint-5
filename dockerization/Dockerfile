FROM python:3.11

WORKDIR /app

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./src /app

COPY ./dockerization/prestart.sh /prestart.sh
RUN chmod +x /prestart.sh

CMD ["/prestart.sh"]

COPY ./dockerization/start.sh /start.sh
RUN chmod +x /prestart.sh

EXPOSE 8000

ENTRYPOINT ["/start.sh"]

