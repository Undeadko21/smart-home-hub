# Smart Kiosk

Веб-приложение для умного дома с интеграцией Home Assistant и AI-ассистентом на базе DeepSeek.

## Описание

Smart Kiosk — это легковесное веб-приложение для управления устройствами умного дома через панель управления (киоск). Приложение предоставляет:

- Интеграцию с **Home Assistant** для управления устройствами
- **AI-ассистент** на основе DeepSeek API для обработки естественного языка
- Кэширование ответов AI для оптимизации запросов
- Очередь уведомлений для различных провайдеров
- Rate limiting для защиты от перегрузки
- Статический веб-интерфейс

## Структура проекта

```
.
├── backend/
│   ├── main.py           # Основной код приложения (FastAPI)
│   ├── requirements.txt  # Зависимости Python
│   └── start.sh          # Скрипт запуска
├── static/
│   └── index.html        # Веб-интерфейс
├── Dockerfile            # Docker-образ приложения
├── docker-compose.yaml   # Конфигурация Docker Compose
└── README.md             # Этот файл
```

## Технологии

- **Backend**: FastAPI, Uvicorn
- **Database**: SQLite
- **HTTP Client**: httpx
- **Rate Limiting**: slowapi
- **Контейнеризация**: Docker, Docker Compose

## Требования

- Docker и Docker Compose
- Доступ к Home Assistant (опционально)
- API ключ DeepSeek (опционально)

## Установка и запуск

### Через Docker Compose (рекомендуется)

1. Отредактируйте `docker-compose.yaml` при необходимости:
   - Укажите путь к директории данных в `volumes`
   - Настройте переменные окружения

2. Запустите контейнер:
```bash
docker-compose up -d
```

3. Приложение будет доступно по адресу: `http://localhost:8080`

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATA_DIR` | Директория для хранения данных (БД, логи, кэш) | `/app/data` |
| `HA_TOKEN` | Токен доступа к Home Assistant | `` |
| `DEEPSEEK_KEY` | API ключ для DeepSeek | `` |

## API

### Home Assistant Integration

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/api/ha/entities` | GET | Получить все устройства или фильтровать по домену (light, switch, climate, cover и т.д.) |
| `/api/ha/entity/{entity_id}` | GET | Получить состояние конкретного устройства |
| `/api/ha/services` | GET | Получить список всех доступных сервисов HA |
| `/api/ha/call_service` | POST | Вызвать сервис HA (domain, service, data, target) |

**Примеры запросов:**

```bash
# Получить все устройства
curl http://localhost:8080/api/ha/entities

# Получить только лампы
curl http://localhost:8080/api/ha/entities?domain=light

# Получить состояние конкретного устройства
curl http://localhost:8080/api/ha/entity/light.living_room

# Включить свет
curl -X POST http://localhost:8080/api/ha/call_service \
  -H "Content-Type: application/json" \
  -d '{"domain":"light","service":"turn_on","data":{"entity_id":"light.living_room"}}'

# Переключить выключатель
curl -X POST http://localhost:8080/api/ha/call_service \
  -H "Content-Type: application/json" \
  -d '{"domain":"switch","service":"toggle","data":{"entity_id":"switch.coffee_maker"}}'
```

### AI Integration

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/api/ai/query` | POST | Отправить запрос к AI-ассистенту |

### Notifications

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/api/notify/test` | POST | Отправить тестовое уведомление |

### System

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/api/health` | GET | Проверка здоровья сервиса |
| `/api/config` | POST | Обновить конфигурацию |

## База данных

Приложение использует SQLite для хранения:

- **config** — Конфигурация приложения
- **ai_cache** — Кэш ответов AI (время жизни: 1 час)
- **notification_queue** — Очередь уведомлений

Путь к БД: `$DATA_DIR/app.db`

## Логирование

Логи сохраняются в: `$DATA_DIR/logs/app.log`

## Ограничения ресурсов (Docker)

В `docker-compose.yaml` настроены ограничения:

- CPU: до 1.0 ядра
- Память: до 512 МБ
- Резервирование: 0.25 CPU, 128 МБ памяти

## Health Check

Контейнер включает проверку здоровья:
- Интервал: 30 секунд
- Таймаут: 5 секунд
- Попытки: 3
- Начальная задержка: 10 секунд

Endpoint: `GET http://localhost:8080/api/health`

## Безопасность

- Запуск от непривилегированного пользователя (UID 1000)
- `no-new-privileges` security option
- Rate limiting для API endpoints

## Лицензия

[Укажите лицензию]

## Контакты

[Укажите контактную информацию]
