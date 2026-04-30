# Установка Smart Kiosk на TrueNAS SCALE 25.10.1 Goldeye

Это руководство описывает, как установить приложение Smart Kiosk на TrueNAS SCALE версии 25.10.1 (Goldeye) через интерфейс Apps с использованием Docker Compose.

## Предварительные требования

- TrueNAS SCALE версии **25.10.1 (Goldeye)** или новее
- Настроенный каталог приложений (Apps)
- Доступ в интернет (для загрузки образа и работы AI)
- Docker и Docker Compose установлены (встроены в TrueNAS SCALE 25.10.1+)

## Структура проекта

```
/workspace/
├── chart/                    # Helm chart для TrueNAS
│   ├── Chart.yaml           # Метаданные приложения (обновлено для 25.10.1)
│   ├── values.yaml          # Значения по умолчанию
│   ├── item.yaml            # Конфигурация для каталога (обновлено для 25.10.1)
│   ├── README.md            # Документация для пользователей
│   ├── INSTALL.md           # Техническая документация
│   ├── questions/
│   │   └── questions.yaml   # Форма настройки в интерфейсе (обновлено для 25.10.1)
│   └── templates/
│       ├── deployment.yaml  # Kubernetes Deployment
│       ├── service.yaml     # Kubernetes Service
│       └── pvc.yaml         # PersistentVolume
├── Dockerfile               # Docker образ приложения
├── docker-compose.yaml      # Конфигурация Docker Compose (обновлено)
└── backend/                 # Исходный код приложения
```

## Способ 1: Установка через интерфейс Apps (рекомендуется для TrueNAS SCALE 25.10.1+)

TrueNAS SCALE 25.10.1 Goldeye поддерживает установку приложений через Docker Compose напрямую через веб-интерфейс.

### Шаг 1: Подготовка Docker Compose файла

1. Создайте директорию для приложения:
```bash
mkdir -p /mnt/data/apps/smart-kiosk
```

2. Скопируйте `docker-compose.yaml` в директорию приложения:
```bash
cp /workspace/docker-compose.yaml /mnt/data/apps/smart-kiosk/
```

3. Отредактируйте `docker-compose.yaml` под ваши нужды:
   - Измените путь к данным в `volumes.source` на нужный вам
   - Настройте переменные окружения (`HA_TOKEN`, `DEEPSEEK_KEY`)
   - При необходимости измените порт в `ports`

### Шаг 2: Установка через веб-интерфейс TrueNAS SCALE 25.10.1

1. Откройте веб-интерфейс TrueNAS SCALE
2. Перейдите в раздел **Apps** → **Discover Apps**
3. Нажмите **Install Application** (или **Custom App** в зависимости от версии интерфейса)
4. Выберите опцию **Docker Compose** или **Compose File**
5. Загрузите файл `docker-compose.yaml` или вставьте его содержимое
6. Настройте параметры через веб-форму:
   - **Port**: 8080 (или другой свободный порт)
   - **Data Storage Path**: `/mnt/data/smart-kiosk` (или ваш путь)
   - **Home Assistant Token**: (опционально) токен доступа
   - **DeepSeek API Key**: (опционально) ключ AI
7. Нажмите **Install** или **Deploy**

### Шаг 3: Проверка установки

1. Перейдите в **Apps** → **Installed Apps**
2. Найдите **smart-kiosk** в списке установленных приложений
3. Проверьте статус — должен быть **Running**
4. Откройте веб-интерфейс по адресу: `http://<IP-адрес-TruNAS>:8080`

## Способ 2: Установка через CLI с помощью Docker Compose

Для пользователей, предпочитающих командную строку или автоматизацию.

### Шаг 1: Подготовка окружения

```bash
# Создайте директорию для приложения
mkdir -p /mnt/data/apps/smart-kiosk

# Перейдите в директорию
cd /mnt/data/apps/smart-kiosk

# Скопируйте docker-compose.yaml
cp /workspace/docker-compose.yaml .
```

### Шаг 2: Настройка конфигурации

Отредактируйте `docker-compose.yaml` с помощью текстового редактора:

```bash
nano docker-compose.yaml
```

Измените следующие параметры:

```yaml
services:
  kiosk:
    ports:
      - "8080:8080"  # Измените первый номер если нужен другой порт
    environment:
      HA_TOKEN: "ваш_токен_home_assistant"  # Опционально
      DEEPSEEK_KEY: "ваш_ключ_deepseek"     # Опционально
    volumes:
      - type: bind
        source: /mnt/data/smart-kiosk  # Измените на ваш путь
        target: /app/data
        bind:
          create_host_path: true
```

### Шаг 3: Создание Docker образа (если не создан)

Если у вас еще нет Docker образа `smart-kiosk:latest`, создайте его:

```bash
# Перейдите в директорию проекта
cd /workspace

# Соберите Docker образ
docker build -t smart-kiosk:latest .
```

### Шаг 4: Запуск приложения

```bash
# Перейдите в директорию с docker-compose.yaml
cd /mnt/data/apps/smart-kiosk

# Запустите приложение в фоновом режиме
docker compose up -d

# Или для старых версий Docker Compose
docker-compose up -d
```

### Шаг 5: Проверка статуса

```bash
# Проверить статус контейнеров
docker compose ps

# Просмотреть логи
docker compose logs -f

# Проверить работу health check
curl http://localhost:8080/api/health
```

### Шаг 6: Управление приложением

```bash
# Остановить приложение
docker compose stop

# Запустить приложение
docker compose start

# Перезапустить приложение
docker compose restart

# Остановить и удалить контейнеры (данные сохранятся)
docker compose down

# Полностью удалить включая тома (данные будут удалены!)
docker compose down -v
```

## Способ 3: Добавление в каталог приложений TrueNAS

Для интеграции в официальный каталог приложений TrueNAS SCALE.

### Шаг 1: Подготовка Helm chart

Убедитесь, что все файлы в директории `chart/` обновлены для TrueNAS SCALE 25.10.1:

- `Chart.yaml` — версия Kubernetes и минимальная версия TrueNAS
- `item.yaml` — метаданные приложения
- `questions/questions.yaml` — форма настройки

### Шаг 2: Размещение chart в каталоге

1. Создайте репозиторий Git с вашим chart
2. Добавьте URL репозитория в TrueNAS:
   - **Apps** → **Manage Catalogs** → **Add Catalog**
   - Укажите URL репозитория
   - Нажмите **Save**

### Шаг 3: Установка из каталога

1. Перейдите в **Apps** → **Discover Apps**
2. Найдите **Smart Kiosk** в каталоге
3. Нажмите **Install**
4. Настройте параметры через веб-форму
5. Нажмите **Install**

## Обновление приложения

### Через Docker Compose

```bash
# Перейдите в директорию приложения
cd /mnt/data/apps/smart-kiosk

# Обновите образ (если используется remote image)
docker compose pull

# Пересоздайте контейнер с новым образом
docker compose up -d --force-recreate

# Или полностью пересоберите (для локальных образов)
docker build -t smart-kiosk:latest /workspace
docker compose up -d --force-recreate
```

### Через интерфейс TrueNAS

1. Перейдите в **Apps** → **Installed Apps**
2. Выберите **Smart Kiosk**
3. Если доступна новая версия, нажмите **Update**
4. Подтвердите обновление

Все данные сохраняются при обновлении благодаря привязанным томам.

## Мониторинг и логи

### Просмотр логов через Docker Compose

```bash
# Просмотр логов в реальном времени
docker compose logs -f

# Просмотр последних 100 строк
docker compose logs --tail=100

# Логи только для конкретного сервиса
docker compose logs kiosk
```

### Просмотр логов через интерфейс TrueNAS

1. **Apps** → **Installed Apps** → **Smart Kiosk**
2. Перейдите на вкладку **Logs**
3. Или через CLI:
```bash
kubectl logs -n ix-smart-kiosk deploy/smart-kiosk-kiosk
```

### Проверка состояния

```bash
# Проверка статуса контейнера
docker compose ps

# Проверка health check
curl http://localhost:8080/api/health

# Детальная информация о контейнере
docker inspect smart-kiosk
```

## Управление данными

Данные приложения хранятся в:
- `<DATA_PATH>/app.db` — база данных
- `<DATA_PATH>/logs/app.log` — логи
- `<DATA_PATH>/cache/` — кэш AI ответов

### Резервное копирование

```bash
# Создайте резервную копию данных
tar -czf smart-kiosk-backup-$(date +%Y%m%d).tar.gz /mnt/data/smart-kiosk

# Восстановление из резервной копии
tar -xzf smart-kiosk-backup-20250101.tar.gz -C /mnt/data/
```

## Удаление приложения

### Через Docker Compose

```bash
# Остановить и удалить контейнеры (данные сохранятся)
docker compose down

# Полностью удалить включая тома (данные будут удалены!)
docker compose down -v

# Удалить директорию данных вручную
rm -rf /mnt/data/smart-kiosk
```

### Через интерфейс TrueNAS

1. **Apps** → **Installed Apps** → **Smart Kiosk**
2. Нажмите **Delete**
3. Подтвердите удаление

**Важно**: Данные могут сохраниться на хосте. Для полного удаления удалите директорию данных вручную.

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

1. Проверьте правильность URL и токена
2. Убедитесь, что Home Assistant доступен из сети TrueNAS
3. Проверьте firewall правила

### AI не работает

1. Проверьте наличие API ключа DeepSeek
2. Убедитесь в наличии доступа в интернет
3. Проверьте лимиты API ключа

### Проблемы с ресурсами

1. Проверьте использование ресурсов:
```bash
docker stats smart-kiosk
```

2. При необходимости измените лимиты в `docker-compose.yaml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Увеличьте лимит CPU
      memory: 1G       # Увеличьте лимит памяти
```

## Дополнительная информация

- [Документация TrueNAS SCALE 25.10.1](https://www.truenas.com/docs/scale/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Helm Chart Documentation](https://helm.sh/docs/)

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `DATA_DIR` | Директория данных | `/app/data` |
| `HA_URL` | Home Assistant URL | `` |
| `HA_TOKEN` | Home Assistant токен | `` |
| `DEEPSEEK_KEY` | DeepSeek API ключ | `` |

## Технические характеристики

- **Минимальная версия TrueNAS SCALE**: 25.10.1 (Goldeye)
- **Версия Kubernetes**: >= 1.25.0
- **Тип приложения**: Docker Compose
- **Порт по умолчанию**: 8080
- **Лимит CPU**: 1.0 ядра
- **Лимит памяти**: 512 МБ
- **Хранилище**: Host path binding
