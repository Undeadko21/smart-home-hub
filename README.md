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
├── chart/                # Helm chart для Kubernetes/TrueNAS
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── templates/
│   └── questions/
├── Dockerfile            # Docker-образ приложения
├── docker-compose.yaml   # Конфигурация Docker Compose
├── README.md             # Этот файл
├── INSTALL.md            # Общая инструкция по установке
├── INSTALL_PROXMOX.md    # Инструкция для Proxmox VE
├── INSTALL_IX_APP.md     # Инструкция для TrueNAS Apps
└── INSTALL_TRUENAS.md    # Инструкция для TrueNAS через терминал
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

### Быстрая установка (рекомендуется)

Запустите скрипт автоматической установки:

```bash
curl -fsSL https://raw.githubusercontent.com/your-repo/smart-kiosk/main/install.sh | bash
```

Или скачайте и запустите вручную:

```bash
wget https://raw.githubusercontent.com/your-repo/smart-kiosk/main/install.sh
chmod +x install.sh
./install.sh
```

Скрипт автоматически:
- Проверит наличие Docker и Docker Compose
- Создаст директорию для данных
- Создаст файл `.env` с настройками по умолчанию
- Соберёт и запустит контейнер

### Через Docker Compose (вручную)

1. Отредактируйте `docker-compose.yaml` при необходимости:
   - Укажите путь к директории данных в `volumes`
   - Настройте переменные окружения

2. Запустите контейнер:
```bash
docker compose up -d --build
```

3. Приложение будет доступно по адресу: `http://localhost:8080`

### Установка на Proxmox VE

Для установки на Proxmox VE (LXC контейнер или VM) следуйте инструкции:
- [INSTALL_PROXMOX.md](INSTALL_PROXMOX.md) - Полная инструкция по установке на Proxmox

### Установка на TrueNAS SCALE

Для установки на TrueNAS SCALE следуйте инструкциям:
- [INSTALL_IX_APP.md](INSTALL_IX_APP.md) - Установка через интерфейс Apps
- [INSTALL_TRUENAS.md](INSTALL_TRUENAS.md) - Установка через терминал

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATA_DIR` | Директория для хранения данных (БД, логи, кэш) | `/app/data` |
| `HA_TOKEN` | Токен доступа к Home Assistant | `` |
| `DEEPSEEK_KEY` | API ключ для DeepSeek | `` |

## API

Приложение предоставляет следующие конечные точки:

- `GET /` — Статический веб-интерфейс
- `GET /api/health` — Проверка здоровья сервиса
- Другие API эндпоинты для взаимодействия с Home Assistant и AI

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

## Поддерживаемые платформы

- **Docker/Docker Compose** - Универсальный способ для любой ОС с поддержкой Docker
- **Proxmox VE** - LXC контейнеры и виртуальные машины (см. [INSTALL_PROXMOX.md](INSTALL_PROXMOX.md))
- **TrueNAS SCALE** - Установка через Apps или терминал (см. [INSTALL_IX_APP.md](INSTALL_IX_APP.md), [INSTALL_TRUENAS.md](INSTALL_TRUENAS.md))
- **Kubernetes** - Через Helm chart в директории `chart/`

---

## Лицензия

[Укажите лицензию]

## Контакты

[Укажите контактную информацию]
