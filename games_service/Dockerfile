# =========================
# 1. BASE
# =========================

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app


# =========================
# 2. BUILDER
# =========================

FROM base AS builder

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --prefix=/install \
    -r requirements.txt


# =========================
# 3. RUNTIME
# =========================

FROM base AS runtime

COPY --from=builder /install /usr/local

COPY app ./app
COPY config ./config
COPY main.py .

EXPOSE 8003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
