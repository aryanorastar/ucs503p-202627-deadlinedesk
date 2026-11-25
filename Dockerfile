FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY code ./code
ENV DEADLINEDESK_DEBUG=0 DEADLINEDESK_DB=/data/db.sqlite3 DEADLINEDESK_MEDIA=/data/media
RUN mkdir /data && DEADLINEDESK_SECRET_KEY=build-only python code/manage.py collectstatic --noinput
EXPOSE 8000
CMD ["sh", "-c", "python code/manage.py migrate --noinput && gunicorn --chdir code deadlinedesk.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --access-logfile -"]
