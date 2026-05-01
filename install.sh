#!/bin/bash
set -e

echo "🚀 Установка Smart Kiosk..."

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не найден. Установите Docker первым."
    exit 1
fi

if ! command -v docker compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose не найден. Установите Docker Compose первым."
    exit 1
fi

# Создание директории для данных
DATA_DIR="${DATA_PATH:-/mnt/data/smart-kiosk}"
echo "📁 Создание директории для данных: $DATA_DIR"
sudo mkdir -p "$DATA_DIR"
sudo chown -R 1000:1000 "$DATA_DIR" 2>/dev/null || true

# Загрузка .env если нет
if [ ! -f .env ]; then
    echo "📝 Создание файла .env с настройками по умолчанию..."
    cat > .env << 'EOF'
# Порт доступа (по умолчанию 8080)
PORT=8080

# Путь к данным
DATA_PATH=/mnt/data/smart-kiosk

# Home Assistant (опционально)
HA_URL=
HA_TOKEN=

# DeepSeek API ключ (опционально)
DEEPSEEK_KEY=

# Лимиты ресурсов
CPU_LIMIT=1.0
MEMORY_LIMIT=512M

# Политика перезапуска
RESTART_POLICY=unless-stopped

# Логирование
LOG_DRIVER=json-file
MAX_LOG_SIZE=10m
MAX_LOG_FILES=3
DISABLE_HEALTHCHECK=false
COMPOSE_PROJECT_NAME=smart-kiosk
EOF
    echo "✅ Файл .env создан. Отредактируйте его при необходимости."
fi

# Сборка и запуск контейнера
echo "🐳 Сборка и запуск контейнера..."
docker compose build --pull
docker compose up -d

# Ожидание запуска
echo "⏳ Ожидание запуска сервиса..."
sleep 5

# Проверка статуса
if docker compose ps | grep -q "running"; then
    PORT=$(grep "^PORT=" .env | cut -d'=' -f2 | tr -d '"' || echo "8080")
    echo ""
    echo "✅ Smart Kiosk успешно установлен и запущен!"
    echo "🌐 Доступен по адресу: http://localhost:$PORT"
    echo ""
    echo "Полезные команды:"
    echo "  docker compose logs -f     # Просмотр логов"
    echo "  docker compose down        # Остановка"
    echo "  docker compose restart     # Перезапуск"
else
    echo "❌ Контейнер не запустился. Проверьте логи:"
    docker compose logs
    exit 1
fi
