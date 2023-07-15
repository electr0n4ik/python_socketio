
chmod +x bash.sh


ssh -R 80:localhost:5000 localhost.run

./bash.sh | npx lt --port 5000

npx localtunnel --port 5000
