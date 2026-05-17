FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
COPY hero.png /usr/share/nginx/html/hero.png
EXPOSE 80
