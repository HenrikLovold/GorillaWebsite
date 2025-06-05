docker build . -t gorillaserver && docker run -d -p 80:80 --name gorilla-app gorillaserver 
