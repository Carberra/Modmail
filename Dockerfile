FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc build-essential python3-dev libxslt-dev libffi-dev libssl-dev

COPY requirements.txt ./
RUN pip install -U pip
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "-m", "modmail"]
