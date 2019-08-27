FROM python:3.7-alpine
COPY requirements.txt /
RUN pip install -r requirements.txt
WORKDIR /src
COPY . /src
ENTRYPOINT ["python", "controller.py"]
