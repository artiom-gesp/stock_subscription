FROM python:3.7

WORKDIR /stock_subscriber

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip3 install pandas uvloop lxml bcrypt

COPY ./requirements.txt .

RUN pip3 install -r /stock_subscriber/requirements.txt

COPY . /stock_subscriber

RUN pip3 install -e .

CMD ["./wait-for-it.sh", "stock_db:3306", "--timeout=30", "--", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000", "--use-colors"]
