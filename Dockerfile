FROM python:alpine

WORKDIR /OLXparser

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "olx_parser.py"]