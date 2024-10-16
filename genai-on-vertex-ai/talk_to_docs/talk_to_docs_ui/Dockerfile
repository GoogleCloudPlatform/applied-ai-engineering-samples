FROM ghcr.io/cirruslabs/flutter:beta AS build

WORKDIR /app

COPY pubspec.* ./

RUN sed -i '/^dev_dependencies:/,/^[^ ]/d' pubspec.yaml

RUN flutter pub get
RUN dart --version
COPY . .

RUN flutter build web --release
# RUN ls
# RUN pwd
# RUN cd build/web
# RUN flutter create output

FROM nginx:stable-alpine

# RUN rm /usr/share/nginx/html/*

COPY nginx.conf /etc/nginx/conf.d/default.conf

# RUN sed -i 's/listen       80;/listen       8080;/g' /etc/nginx/conf.d/default.conf

COPY --from=build /app/build/web /usr/share/nginx/html

EXPOSE 8080

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]