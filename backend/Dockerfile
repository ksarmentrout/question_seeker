FROM python:3.8-slim-buster
WORKDIR /usr/src/app
COPY . $WORKDIR
RUN bash setup_packages.sh
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]