FROM php:8.1-apache

# Install DNS utilities
RUN apt-get update && apt-get install -y dnsutils && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY index.php /var/www/html/

# Set permissions
RUN chown -R www-data:www-data /var/www/html

EXPOSE 80
