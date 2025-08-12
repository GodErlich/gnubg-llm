FROM gitpod/workspace-full:latest

# Install GNU Backgammon and additional dependencies
RUN sudo apt-get update && \
    sudo apt-get install -y gnubg python3-dev && \
    sudo apt-get clean && \
    sudo rm -rf /var/lib/apt/lists/*

# Verify installation
RUN gnubg --version

# Set working directory
WORKDIR /workspace