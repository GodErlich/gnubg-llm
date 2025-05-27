echo "Building gnubg container..."
docker build -t gnubg-app .

echo "Running gnubg container..."
docker run -it --rm \
    -v $(pwd)/output:/app/output \
    -v $(pwd)/input:/app/input \
    gnubg-app
