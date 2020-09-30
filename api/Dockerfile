FROM python:3.7-alpine

ENV API_DIR="/app"
ENV LOG_FILE="${API_DIR}/app.log"
ENV CRON_TASK="* * * * *"

WORKDIR ${API_DIR}

COPY . ${API_DIR}
RUN pip install -r requirements.txt
RUN echo "${CRON_TASK} python ${API_DIR}/open_weather.py >> ${LOG_FILE} 2>&1" > ${API_DIR}/crontab
RUN touch ${LOG_FILE}
RUN crontab ${API_DIR}/crontab
RUN crontab -l

CMD crond && tail -f ${LOG_FILE}
