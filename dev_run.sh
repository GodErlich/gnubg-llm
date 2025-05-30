echo "Running gnubg with live file changes (no rebuild needed)..."
docker run -it --rm \
    -v $(pwd)/output:/app/output \
    -v $(pwd)/input:/app/input \
    -v $(pwd)/llm_version.py:/app/llm_version.py \
    -v $(pwd)/.env:/app/.env \
    gnubg-app

