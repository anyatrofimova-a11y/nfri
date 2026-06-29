FROM nginx:1.27-alpine

COPY deploy/nginx.conf /etc/nginx/nginx.conf
COPY site/ /usr/share/nginx/html/

EXPOSE 8080
