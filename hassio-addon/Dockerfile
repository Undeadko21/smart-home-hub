FROM python:3.11-alpine AS builder
WORKDIR /build
COPY hassio-addon/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-alpine
RUN apk add --no-cache curl sqlite bash
WORKDIR /app
COPY --from=builder /install /usr/local
COPY backend/ ./backend/
COPY static/ ./static/
COPY hassio-addon/run.sh ./run.sh
RUN chmod +x run.sh && chown -R 1000:1000 /app
USER 1000:1000
EXPOSE 8080
ENV DATA_DIR=/data
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:8080/api/health || exit 1
CMD ["./run.sh"]
