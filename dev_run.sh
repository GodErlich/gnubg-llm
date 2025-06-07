echo "Running last build (rebuild needed only after changes)..."
docker run -it --rm \
    -v $(pwd)/output:/app/output \
    -v $(pwd)/input:/app/input \
    -v $(pwd)/main.py:/app/main.py \
    -v $(pwd)/.env:/app/.env \
    gnubg-app

