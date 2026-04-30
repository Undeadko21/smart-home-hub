FROM python:3.11-alpine AS builder
WORKDIR /build
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-alpine
RUN apk add --no-cache curl sqlite
WORKDIR /app
COPY --from=builder /install /usr/local
COPY backend/ ./backend/
COPY static/ ./static/
COPY backend/start.sh ./
RUN chmod +x start.sh && chown -R 1000:1000 /app
USER 1000:1000
EXPOSE 8080
ENV DATA_DIR=/app/data
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:8080/api/health || exit 1
CMD ["./start.sh"]
