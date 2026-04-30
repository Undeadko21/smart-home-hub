# Установка Smart Kiosk через ix-app (TrueNAS SCALE Apps)

Это руководство описывает установку приложения Smart Kiosk через интерфейс **Apps** (ix-app) в TrueNAS SCALE.

## Предварительные требования

- TrueNAS SCALE версии **25.10.1 (Goldeye)** или новее
- Настроенный каталог приложений (**Apps**)
- Доступ в интернет для загрузки Docker-образа
- Свободный порт для доступа к приложению (по умолчанию 8080)

---

## Способ 1: Установка из каталога приложений (рекомендуется)

### Шаг 1: Добавление каталога с приложением

1. Откройте веб-интерфейс TrueNAS SCALE
2. Перейдите в раздел **Apps** → **Manage Catalogs**
3. Нажмите **Add Catalog**
4. Заполните форму:
   - **Name**: `smart-kiosk`
   - **Repository URL**: `https://github.com/YOUR_USERNAME/smart-kiosk.git`
   - **Branch**: `main`
5. Нажмите **Save**

> **Примечание**: Замените `YOUR_USERNAME` на ваше имя пользователя GitHub

### Шаг 2: Установка приложения

1. Перейдите в **Apps** → **Discover Apps**
2. Найдите **Smart Kiosk** в списке доступных приложений
3. Нажмите **Install**

### Шаг 3: Настройка параметров

#### Basic Configuration (Основные настройки)

| Параметр | Описание | Рекомендуемое значение |
|----------|----------|----------------------|
| **Порт приложения** | Порт для доступа к веб-интерфейсу | `8080` |
| **Путь хранения данных** | Директория на хосте для данных | `/mnt/data/smart-kiosk` |
| **Лимит CPU** | Максимальное количество ядер CPU | `1.0` |
| **Лимит памяти** | Максимальный объем RAM | `512M` |

#### Home Assistant Integration (Интеграция с Home Assistant)

| Параметр | Описание | Пример |
|----------|----------|--------|
| **Home Assistant URL** | URL вашего сервера HA | `http://192.168.1.100:8123` |
| **Home Assistant Token** | Long-Lived Access Token | `ваш_токен` |

> **Как получить токен Home Assistant:**
> 1. Откройте Home Assistant
> 2. Перейдите в **Профиль** → **Long-Lived Access Tokens**
> 3. Создайте новый токен с именем `smart-kiosk`
> 4. Скопируйте и сохраните токен

#### AI Settings (Настройки AI)

| Параметр | Описание |
|----------|----------|
| **DeepSeek API Key** | API ключ для AI-ассистента (опционально) |

#### Docker Compose Settings (Настройки Docker)

| Параметр | Описание | Значение по умолчанию |
|----------|----------|----------------------|
| **Имя проекта** | Имя для контейнеров | `smart-kiosk` |
| **Политика перезапуска** | Поведение при сбоях | `Unless Stopped` |
| **Проверка здоровья** | Мониторинг состояния | `Включено` |
| **Драйвер логов** | Тип логирования | `JSON File` |
| **Размер логов** | Макс. размер файла | `10m` |
| **Кол-во файлов логов** | Файлов для ротации | `3` |

### Шаг 4: Завершение установки

1. Проверьте все введенные параметры
2. Нажмите **Install**
3. Дождитесь завершения установки (статус изменится на **Running**)

---

## Способ 2: Установка через Docker Compose в интерфейсе Apps

TrueNAS SCALE 25.10.1+ поддерживает установку через Docker Compose напрямую.

### Шаг 1: Подготовка docker-compose.yaml

Создайте файл `docker-compose.yaml` со следующим содержимым:

```yaml
services:
  kiosk:
    image: smart-kiosk:latest
    container_name: smart-kiosk
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - DATA_DIR=/app/data
      - HA_URL=http://192.168.1.100:8123
      - HA_TOKEN=your_home_assistant_token
      - DEEPSEEK_KEY=your_deepseek_api_key
    volumes:
      - type: bind
        source: /mnt/data/smart-kiosk
        target: /app/data
        bind:
          create_host_path: true
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
```

### Шаг 2: Установка через интерфейс

1. Откройте **Apps** → **Discover Apps**
2. Нажмите **Install Application** или **Custom App**
3. Выберите опцию **Docker Compose** / **Compose File**
4. Загрузите файл `docker-compose.yaml` или вставьте его содержимое
5. При необходимости отредактируйте параметры через веб-форму:
   - Измените порт если 8080 занят
   - Укажите ваш путь для данных
   - Введите токены Home Assistant и DeepSeek
6. Нажмите **Install** / **Deploy**

---

## Способ 3: Установка через YAML (для продвинутых пользователей)

### Шаг 1: Создание файла значений

Создайте файл `smart-kiosk-values.yaml`:

```yaml
# Базовые настройки
PORT: 8080
DATA_PATH: "/mnt/data/smart-kiosk"
CPU_LIMIT: "1.0"
MEMORY_LIMIT: "512M"

# Home Assistant
HA_URL: "http://192.168.1.100:8123"
HA_TOKEN: "your_long_lived_token"

# AI настройки
DEEPSEEK_KEY: "your_deepseek_api_key"

# Docker Compose настройки
COMPOSE_PROJECT_NAME: "smart-kiosk"
RESTART_POLICY: "unless-stopped"
ENABLE_HEALTHCHECK: true
LOG_DRIVER: "json-file"
MAX_LOG_SIZE: "10m"
MAX_LOG_FILES: 3
```

### Шаг 2: Установка через CLI

```bash
# Клонировать репозиторий
git clone https://github.com/YOUR_USERNAME/smart-kiosk.git
cd smart-kiosk

# Установить приложение
helm install smart-kiosk ./chart \
  --namespace ix-smart-kiosk \
  --create-namespace \
  -f smart-kiosk-values.yaml
```

---

## Проверка установки

### Через веб-интерфейс

1. Перейдите в **Apps** → **Installed Apps**
2. Найдите **Smart Kiosk** в списке
3. Проверьте статус — должен быть **Running**
4. Откройте веб-интерфейс по адресу: `http://<IP-адрес-TruNAS>:8080`

### Через CLI

```bash
# Проверить статус контейнера
docker compose ps

# Просмотреть логи
docker compose logs -f

# Проверить health check
curl http://localhost:8080/api/health
```

---

## Управление приложением

### Обновление приложения

#### Через интерфейс TrueNAS:

1. **Apps** → **Installed Apps**
2. Выберите **Smart Kiosk**
3. Если доступна новая версия, нажмите **Update**
4. Подтвердите обновление

#### Через CLI:

```bash
# Перейдите в директорию приложения
cd /mnt/data/apps/smart-kiosk

# Обновите образ
docker compose pull

# Пересоздайте контейнер
docker compose up -d --force-recreate
```

### Остановка/Запуск

#### Через интерфейс:

1. **Apps** → **Installed Apps** → **Smart Kiosk**
2. Используйте кнопки **Stop** / **Start** / **Restart**

#### Через CLI:

```bash
# Остановить
docker compose stop

# Запустить
docker compose start

# Перезапустить
docker compose restart
```

### Удаление приложения

> **Внимание**: При удалении данные могут сохраниться на хосте!

#### Через интерфейс:

1. **Apps** → **Installed Apps** → **Smart Kiosk**
2. Нажмите **Delete**
3. Подтвердите удаление
4. При необходимости удалите директорию данных вручную:
   ```bash
   rm -rf /mnt/data/smart-kiosk
   ```

#### Через CLI:

```bash
# Остановить и удалить контейнеры (данные сохранятся)
docker compose down

# Полностью удалить включая тома (данные будут удалены!)
docker compose down -v
```

---

## Мониторинг и логи

### Просмотр логов

#### Через интерфейс:

1. **Apps** → **Installed Apps** → **Smart Kiosk**
2. Перейдите на вкладку **Logs**

#### Через CLI:

```bash
# Логи в реальном времени
docker compose logs -f

# Последние 100 строк
docker compose logs --tail=100

# Логи конкретного сервиса
docker compose logs kiosk
```

### Проверка состояния

```bash
# Статус контейнера
docker compose ps

# Детальная информация
docker inspect smart-kiosk

# Использование ресурсов
docker stats smart-kiosk
```

---

## Решение проблем

### Приложение не запускается

1. **Проверьте логи:**
   ```bash
   docker compose logs
   ```

2. **Убедитесь, что порт не занят:**
   ```bash
   netstat -tlnp | grep 8080
   ```

3. **Проверьте права доступа:**
   ```bash
   ls -la /mnt/data/smart-kiosk
   chmod 755 /mnt/data/smart-kiosk
   ```

### Ошибки подключения к Home Assistant

- Проверьте правильность URL и токена
- Убедитесь, что Home Assistant доступен из сети TrueNAS
- Проверьте настройки firewall

### AI не работает

- Проверьте наличие API ключа DeepSeek
- Убедитесь в наличии доступа в интернет
- Проверьте лимиты API ключа

### Проблемы с ресурсами

```bash
# Проверить использование ресурсов
docker stats smart-kiosk

# При необходимости измените лимиты в настройках приложения
```

---

## Резервное копирование данных

Данные приложения хранятся в:
- `<DATA_PATH>/app.db` — база данных
- `<DATA_PATH>/logs/app.log` — логи
- `<DATA_PATH>/cache/` — кэш AI ответов

### Создание резервной копии

```bash
tar -czf smart-kiosk-backup-$(date +%Y%m%d).tar.gz /mnt/data/smart-kiosk
```

### Восстановление из резервной копии

```bash
tar -xzf smart-kiosk-backup-20250101.tar.gz -C /mnt/data/
```

---

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `DATA_DIR` | Директория данных внутри контейнера | `/app/data` |
| `HA_URL` | Home Assistant URL | `` |
| `HA_TOKEN` | Home Assistant токен | `` |
| `DEEPSEEK_KEY` | DeepSeek API ключ | `` |

---

## Технические характеристики

- **Минимальная версия TrueNAS SCALE**: 25.10.1 (Goldeye)
- **Версия Kubernetes**: >= 1.25.0
- **Тип приложения**: Helm chart / Docker Compose
- **Порт по умолчанию**: 8080
- **Лимит CPU**: 1.0 ядра
- **Лимит памяти**: 512 МБ
- **Хранилище**: Host path binding

---

## Дополнительная информация

- [Документация TrueNAS SCALE](https://www.truenas.com/docs/scale/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Helm Chart Documentation](https://helm.sh/docs/)
