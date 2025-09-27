# STAGE 1: Base build stage
FROM python:3.13-bookworm AS builder

RUN mkdir /app

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY ./requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# Install Firefox
RUN wget https://ftp.mozilla.org/pub/firefox/releases/143.0/linux-x86_64/en-US/firefox-143.0.tar.xz && \
    tar -xf firefox-143.0.tar.xz 

# Install Geckodriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz && \
    tar -xf geckodriver-v0.36.0-linux64.tar.gz 

# STAGE 2: Production stage
FROM python:3.13-slim

RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY --from=builder /app/firefox/ /usr/lib/firefox/
COPY --from=builder /app/geckodriver /app/geckodriver

WORKDIR /app

COPY --chown=appuser:appuser . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

USER appuser

CMD ["python", "scrape.py"]