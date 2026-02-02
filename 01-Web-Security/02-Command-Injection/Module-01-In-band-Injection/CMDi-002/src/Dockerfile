FROM php:8.1-apache

# Create document directory with sample files
RUN mkdir -p /var/www/docs && \
    echo "This is a sample document.\n\nLorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." > /var/www/docs/sample.txt && \
    echo "Company Policy Document\n\nSection 1: Introduction\nThis document outlines the company policies..." > /var/www/docs/policy.txt && \
    echo "Meeting Notes - Q4 2024\n\nAttendees: John, Jane, Bob\nTopics discussed: Budget, Projects" > /var/www/docs/notes.txt

# Copy application files
COPY index.php /var/www/html/

# Set permissions
RUN chown -R www-data:www-data /var/www/html /var/www/docs

EXPOSE 80
