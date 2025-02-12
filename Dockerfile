FROM --platform=linux/amd64 python:3.11 as build

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt


COPY . .

EXPOSE 8000

COPY entrypoint_app.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint_app.sh

ENTRYPOINT ["/usr/src/app/entrypoint_app.sh"]



