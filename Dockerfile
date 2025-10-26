# syntax=docker/dockerfile:1.4
FROM python:3.9-slim

WORKDIR /app

# system deps needed for many ML libs and execstack (optional)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl ca-certificates git \
    libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# copy only requirements first -> better cache
COPY requirements.txt /app/requirements.txt

# Use BuildKit cache for pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r /app/requirements.txt

# copy app last so changes to code don't bust dependency cache
COPY . /app

# OPTIONAL: if you want to try clearing executable-stack bit for libtorch_cpu.so
# (may require package 'execstack' in your distro; remove if not available)
RUN apt-get update && apt-get install -y --no-install-recommends execstack && \
    if [ -f "/usr/local/lib/python3.9/site-packages/torch/lib/libtorch_cpu.so" ]; then \
      execstack -s /usr/local/lib/python3.9/site-packages/torch/lib/libtorch_cpu.so || true ; \
    fi && \
    apt-get remove -y execstack && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
EXPOSE 5000
CMD ["python", "app.py"]