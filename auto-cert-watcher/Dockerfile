FROM php:8.2-cli-alpine

RUN apk add --no-cache \
    php82-pdo \
    php82-pdo_mysql \
    php82-redis \
    && docker-php-ext-install pdo pdo_mysql \
    && pecl install redis && docker-php-ext-enable redis

WORKDIR /app
COPY watcher.php .

CMD ["php", "-d", "display_errors=1", "watcher.php"]
