# Use the official Ubuntu image as the base image
FROM ubuntu:latest

# Set environment variables to avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    unzip \
    tk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install tkinter explicitly to resolve the missing module error
RUN apt-get update && apt-get install -y python3-tk && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the testfiles directory to /tmp/TestFiles
COPY test/TestFiles /tmp/TestFiles

# Create a virtual environment and install Python dependencies
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Set the virtual environment as the default Python environment
ENV PATH="/app/venv/bin:$PATH"

# Run the Python scripts as tests during the build process
RUN /bin/bash -c "set -e; python3 main.py /tmp/TestFiles/TestFile0.kdbx 'verySecurePassword0'"
RUN /bin/bash -c "set -e; python3 main.py /tmp/TestFiles/TestFile1.kdbx 'verySecurePassword1'"
RUN /bin/bash -c "set -e; python3 main.py /tmp/TestFiles/TestAbsoluteKdbx.kdbx 'verySecurePassword2'"
RUN /bin/bash -c "set -e; python3 main.py /tmp/TestFiles/TestAbsoluteKdbxShare.kdbx.share 'verySecurePassword3'"
RUN /bin/bash -c "set -e; python3 main.py /tmp/TestFiles/TestRelativeKdbx.kdbx 'verySecurePassword4'"
RUN /bin/bash -c "set -e; python3 main.py /tmp/TestFiles/TestRelativeKdbxShare.kdbx.share 'verySecurePassword5'"

# Set /bin/bash as the default entrypoint
ENTRYPOINT ["/bin/bash"]