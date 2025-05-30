echo "Starting interactive gnubg session..."
docker run -it --rm \
    -v $(pwd)/output:/app/output \
    -v $(pwd)/input:/app/input \
    -v $(pwd)/llm_version.py:/app/llm_version.py \
    -v $(pwd)/.env:/app/.env \
    gnubg-app gnubg -t