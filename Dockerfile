# Use Ubuntu as base image (gnubg works well on Linux)
FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update package list and install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
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
    libpq-dev \
    libmysqlclient-dev \
    swig \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Clone gnubg with shallow clone for faster download (only the specific tag)
RUN git clone --depth 1 --branch release-1_08_003 https://git.savannah.gnu.org/git/gnubg.git

# Check what we got
RUN cd gnubg && git log --oneline -5

# Run autogen with debug output
RUN cd gnubg && ./autogen.sh

# Configure with Python support enabled (like Windows gnubg.exe)
RUN cd gnubg && ./configure --without-gtk --enable-simd=sse2 --enable-python

# Make with debug output
RUN cd gnubg && make

# Install
RUN cd gnubg && make install

# Cleanup
RUN rm -rf gnubg

# Install Python dependencies with debug output and error handling
COPY requirements.txt .
RUN echo "Contents of requirements.txt:" && cat requirements.txt
RUN pip3 install --upgrade pip

# Install other packages (no need for PyPI gnubg - using embedded Python)
RUN pip3 install python-dotenv requests || true
RUN pip3 install ipython colorama || true
RUN pip3 install PyGreSQL PyMySQL || echo "Database libraries failed - continuing without them"
RUN pip3 install --no-cache-dir -r requirements.txt || echo "Some packages failed - continuing"

# Copy your Python script and configuration files
COPY .env .
COPY main.py .

## TODO: instead of copying all files one by one, move all to a specific directory, named src.
COPY src/ /app/src/

# Set environment variables for gnubg
ENV GNUBG_DIR=/usr/local/share/gnubg
ENV PATH="/usr/local/bin:${PATH}"

# Create gnubg user directory
RUN mkdir -p /root/.gnubg && \
    cp -r /root/.gnubg/ 2>/dev/null || true

# Make sure gnubg can find its data files
RUN gnubg --version || true

# Set the default command to run your script through gnubg (like Windows)
CMD ["gnubg", "-t", "-p", "main.py"]