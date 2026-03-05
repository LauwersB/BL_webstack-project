FROM sebp/lighttpd:latest

# Kopieer je website bestanden
COPY index.html /var/www/localhost/htdocs/
COPY style.css /var/www/localhost/htdocs/

# Kopieer de nieuwe configuratie
COPY lighttpd.conf /etc/lighttpd/lighttpd.conf

EXPOSE 80