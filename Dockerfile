FROM ubuntu/apache2

# Copy website stuff
COPY ./index.html ~
COPY ./index.html /var/www/html/
COPY ./findscript.js /var/www/html/
COPY ./styles.css /var/www/html/
COPY ./gorilla_analyze.py /var/www/html/
COPY ./gorillaparser.py /var/www/html/
COPY ./time_plotter.py /var/www/html/
COPY ./plots/ /var/www/html/plots/
COPY ./logger.py /var/www/html/

# Set workdir
WORKDIR /var/www/html

# Setup web hosting
RUN chown -R www-data:www-data /var/www/html

# Install apache, python3, curl
RUN apt update
RUN apt install php libapache2-mod-php -y
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN apt install python3.12-venv -y
RUN apt-get install ca-certificates curl -y

# Get Python modules
RUN alias python='python3'
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install regex
RUN pip install google-auth-oauthlib
RUN pip install google-api-python-client
RUN pip install matplotlib

# Install node and vue
RUN curl -sL https://deb.nodesource.com/setup_16.x -o /tmp/nodesource_setup.sh
RUN bash /tmp/nodesource_setup.sh
RUN apt install nodejs -y
RUN apt-get install aptitude -y
RUN aptitude install npm -y
RUN npm install -g @vue/cli

# Run update script
RUN nohup python -u /var/www/html/gorilla_analyze server > /var/www/html/analyzer.log 2>&1 &

# Expose port
EXPOSE 80
CMD ["apache2ctl", "-D", "FOREGROUND"]
