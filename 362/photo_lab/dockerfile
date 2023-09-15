FROM python:3.9

RUN apt-get update

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY ./src .

CMD ["python","-c", "from main import PLAB; PLAB.WebApp()"]