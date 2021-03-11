FROM python:3.9-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apk add --no-cache gcc musl-dev tzdata
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9993

CMD [ "python", "./main.py" ]