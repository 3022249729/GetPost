FROM nginx

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./getpost_pro.crt /etc/nginx/
COPY ./server.key /etc/nginx/
RUN mkdir /etc/nginx/public
