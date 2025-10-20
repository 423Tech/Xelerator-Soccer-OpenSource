FROM python:3.12.9-slim

WORKDIR /home/CeasearKit/src/

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ..src ./src
CMD ["python", "/main.py"]