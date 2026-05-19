FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
COPY hero.png /usr/share/nginx/html/hero.png
COPY favicon.png /usr/share/nginx/html/favicon.png
EXPOSE 80
