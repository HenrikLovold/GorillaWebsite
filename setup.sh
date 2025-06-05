docker build . -t gorillaserver && docker run -d -p 80:80 --name gorilla-app gorillaserver && docker cp *.json gorilla-app:/var/www/html 
