# Use Ubuntu as base image (gnubg works well on Linux)
FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update package list and install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    wget \
    build-essential \
    automake \
    autoconf \
    libtool \
    pkg-config \
    libglib2.0-dev \
    libgtk-3-dev \
    libcairo2-dev \
    libreadline-dev \
    libxml2-dev \
    libxslt1-dev \
    flex \
    bison \
    texinfo \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Clone gnubg with shallow clone for faster download (only the specific tag)
RUN git clone --depth 1 --branch release-1_08_003 https://git.savannah.gnu.org/git/gnubg.git

# Check what we got
RUN cd gnubg && git log --oneline -5

# Run autogen with debug output
RUN cd gnubg && ./autogen.sh

# Configure with debug output  
RUN cd gnubg && ./configure --without-gtk --enable-simd=sse2

# Make with debug output
RUN cd gnubg && make

# Install
RUN cd gnubg && make install

# Cleanup
RUN rm -rf gnubg

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy your Python script and configuration files
COPY your_script.py .
COPY .env .
COPY gnubg_config/ ./gnubg_config/

# Set environment variables for gnubg
ENV GNUBG_DIR=/usr/local/share/gnubg
ENV PATH="/usr/local/bin:${PATH}"

# Create gnubg user directory and copy configs
RUN mkdir -p /root/.gnubg && \
    cp -r gnubg_config/* /root/.gnubg/ 2>/dev/null || true

# Make sure gnubg can find its data files
RUN gnubg --version || true

# Set the default command
CMD ["python3", "your_script.py"]