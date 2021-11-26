FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc

COPY requirements.txt ./
RUN pip install -U pip
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "-m", "modmail"]
