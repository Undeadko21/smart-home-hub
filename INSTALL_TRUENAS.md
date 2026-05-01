# Установка Smart Kiosk на TrueNAS SCALE через терминал

Это руководство описывает, как установить приложение Smart Kiosk на TrueNAS SCALE **исключительно через терминал** с использованием Docker Compose.

## Предварительные требования

- TrueNAS SCALE с поддержкой Docker и Docker Compose
- Доступ в интернет (для работы AI)
- Свободный порт для доступа к приложению (по умолчанию 8080)

## Структура проекта

```
/workspace/
├── Dockerfile               # Docker образ приложения
├── docker-compose.yaml      # Конфигурация Docker Compose
└── backend/                 # Исходный код приложения
```

## Установка через терминал TrueNAS

### Быстрая установка (одна команда)

Подключитесь к TrueNAS по SSH и выполните:

```bash
mkdir -p /mnt/data/apps/smart-kiosk && cd /mnt/data/apps/smart-kiosk && git clone https://github.com/Undeadko21/smart-home-hub.git . && cat > .env << 'EOF' && docker compose up -d --build
PORT=8080
DATA_PATH=/mnt/data/smart-kiosk
HA_URL=
HA_TOKEN=
DEEPSEEK_KEY=
CPU_LIMIT=1.0
MEMORY_LIMIT=512M
RESTART_POLICY=unless-stopped
COMPOSE_PROJECT_NAME=smart-kiosk
DISABLE_HEALTHCHECK=false
LOG_DRIVER=json-file
MAX_LOG_SIZE=10m
MAX_LOG_FILES=3
EOF
```

После выполнения приложение будет доступно по адресу: `http://<IP-адрес-TruNAS>:8080`

---

### Пошаговая установка

Если вы предпочитаете пошаговый процесс:

#### Шаг 1: Подготовка директории

Подключитесь к TrueNAS по SSH и выполните команды:

```bash
# Создайте директорию для приложения
mkdir -p /mnt/data/apps/smart-kiosk

# Перейдите в директорию
cd /mnt/data/apps/smart-kiosk
```

#### Шаг 2: Клонирование репозитория

```bash
# Клонируйте репозиторий
git clone https://github.com/Undeadko21/smart-home-hub.git .
```

#### Шаг 3: Настройка конфигурации

Создайте файл `.env` с вашими настройками:

```bash
nano .env
```

Вставьте следующее содержимое:

```ini
# Основные настройки
COMPOSE_PROJECT_NAME=smart-kiosk
PORT=8080
DATA_PATH=/mnt/data/smart-kiosk
RESTART_POLICY=unless-stopped

# Лимиты ресурсов
CPU_LIMIT=1.0
MEMORY_LIMIT=512M

# Home Assistant (опционально)
HA_URL=http://192.168.1.100:8123
HA_TOKEN=your_home_assistant_token

# AI настройки (опционально)
DEEPSEEK_KEY=your_deepseek_api_key

# Дополнительные настройки
DISABLE_HEALTHCHECK=false
LOG_DRIVER=json-file
MAX_LOG_SIZE=10m
MAX_LOG_FILES=3
```

Сохраните файл (Ctrl+O, Enter) и выйдите (Ctrl+X).

#### Шаг 4: Создание Docker образа и запуск

```bash
# Соберите Docker образ и запустите приложение
docker compose up -d --build
```

Процесс сборки займёт 2-5 минут.

#### Шаг 5: Проверка статуса

```bash
# Проверить статус контейнеров
docker compose ps

# Просмотреть логи
docker compose logs -f

# Проверить работу health check
curl http://localhost:8080/api/health
```

Ожидаемый результат `docker compose ps`:
```
NAME            STATUS                    PORTS
smart-kiosk     Up (healthy)              0.0.0.0:8080->8080/tcp
```

Откройте браузер и перейдите по адресу: `http://<IP-адрес-TruNAS>:8080`

---

## Управление приложением

### Просмотр логов

```bash
# Логи в реальном времени
docker compose logs -f

# Последние 100 строк
docker compose logs --tail=100

# Логи конкретного сервиса
docker compose logs kiosk
```

### Остановка/Запуск

```bash
# Остановить приложение
docker compose stop

# Запустить приложение
docker compose start

# Перезапустить приложение
docker compose restart
```

### Обновление приложения

```bash
# Перейдите в директорию приложения
cd /mnt/data/apps/smart-kiosk

# Обновите исходный код из Git
git pull origin main

# Пересоберите образ и пересоздайте контейнер
docker compose up -d --build --force-recreate
```

### Удаление приложения

```bash
# Остановить и удалить контейнеры (данные сохранятся)
docker compose down

# Полностью удалить включая тома (данные будут удалены!)
docker compose down -v

# Удалить директорию данных вручную
rm -rf /mnt/data/smart-kiosk
```

## Мониторинг

### Использование ресурсов

```bash
# Статистика использования CPU и памяти
docker stats smart-kiosk
```

### Проверка здоровья

```bash
# Быстрая проверка
curl -f http://localhost:8080/api/health

# Подробная информация о контейнере
docker inspect smart-kiosk | grep -A 20 Health
```

## Решение проблем

### Приложение не запускается

1. Проверьте логи:
```bash
docker compose logs
```

2. Убедитесь, что порт не занят:
```bash
netstat -tlnp | grep 8080
```

3. Проверьте права доступа к директории данных:
```bash
ls -la /mnt/data/smart-kiosk
chmod 755 /mnt/data/smart-kiosk
```

### Ошибки подключения к Home Assistant

- Проверьте правильность URL и токена
- Убедитесь, что Home Assistant доступен из сети TrueNAS
- Проверьте firewall правила

### AI не работает

- Проверьте наличие API ключа DeepSeek
- Убедитесь в наличии доступа в интернет
- Проверьте лимиты API ключа

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `DATA_DIR` | Директория данных | `/app/data` |
| `HA_URL` | Home Assistant URL | `` |
| `HA_TOKEN` | Home Assistant токен | `` |
| `DEEPSEEK_KEY` | DeepSeek API ключ | `` |

## Технические характеристики

- **Порт по умолчанию**: 8080
- **Лимит CPU**: 1.0 ядра
- **Лимит памяти**: 512 МБ
- **Хранилище**: Host path binding
