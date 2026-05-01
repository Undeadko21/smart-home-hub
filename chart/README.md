# Smart Kiosk - Helm Chart для Kubernetes/TrueNAS SCALE

Smart Kiosk — это веб-приложение для управления устройствами умного дома через панель управления (киоск).

## Возможности

- **Интеграция с Home Assistant** — управление устройствами умного дома
- **AI-ассистент на базе DeepSeek** — обработка запросов на естественном языке
- **Кэширование ответов** — оптимизация запросов к AI
- **Очередь уведомлений** — поддержка различных провайдеров уведомлений
- **Rate limiting** — защита от перегрузки API

## Требования

- Kubernetes 1.25+ или TrueNAS SCALE 22.02+
- Helm 3.x
- Доступ к сети (для работы AI и Home Assistant)

## Установка

### Вариант 1: Установка через Helm CLI

```bash
# Клонировать репозиторий
git clone https://github.com/Undeadko21/smart-home-hub.git
cd smart-home-hub/chart

# Установить приложение
helm install smart-kiosk . \
  --namespace ix-smart-kiosk \
  --create-namespace \
  --set ha_url=http://192.168.1.100:8123 \
  --set ha_token=your_home_assistant_token \
  --set deepseek_key=your_deepseek_api_key
```

### Вариант 2: Установка с файлом значений

Создайте файл `values-custom.yaml`:

```yaml
image:
  repository: smart-kiosk
  tag: latest
  pullPolicy: IfNotPresent

ha_url: "http://192.168.1.100:8123"
ha_token: "your_home_assistant_token"
deepseek_key: "your_deepseek_api_key"

service:
  type: LoadBalancer
  port: 8080

storage:
  hostPath: "/mnt/data/smart-kiosk"
  containerPath: "/app/data"

resources:
  limits:
    cpu: "1.0"
    memory: "512M"
  requests:
    cpu: "0.25"
    memory: "128M"
```

Установите с кастомными значениями:

```bash
helm install smart-kiosk . -f values-custom.yaml --namespace ix-smart-kiosk --create-namespace
```

### Вариант 3: Установка на TrueNAS SCALE через интерфейс Apps

1. В интерфейсе TrueNAS перейдите в раздел **Apps**
2. Нажмите **Manage Catalogs** и добавьте новый каталог:
   - **Name**: `smart-kiosk`
   - **Repository URL**: `https://github.com/Undeadko21/smart-home-hub.git`
   - **Branch**: `main`
3. Перейдите в **Discover Apps** и найдите **Smart Kiosk**
4. Нажмите **Install** и настройте параметры через веб-форму

## Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATA_DIR` | Директория для хранения данных | `/app/data` |
| `HA_URL` | URL Home Assistant сервера | `` |
| `HA_TOKEN` | Токен доступа к Home Assistant | `` |
| `DEEPSEEK_KEY` | API ключ DeepSeek | `` |

### Ограничения ресурсов

По умолчанию приложение использует:
- CPU: до 1.0 ядра
- Память: до 512 МБ

Эти значения можно изменить в `values.yaml`.

## Использование

После установки приложение будет доступно по адресу:
```
http://<IP-адрес-кластера>:<порт>
```

Для доступа извне настройте Ingress или используйте Service типа LoadBalancer.

## Обновление

```bash
# Обновите репозиторий
cd smart-home-hub/chart
git pull

# Обновите релиз
helm upgrade smart-kiosk . --namespace ix-smart-kiosk
```

## Удаление

```bash
helm uninstall smart-kiosk --namespace ix-smart-kiosk
```

## Хранение данных

Данные приложения хранятся в директории, указанной в `storage.hostPath`:
- `app.db` — база данных SQLite
- `logs/app.log` — логи приложения
- `cache/` — кэш AI ответов

## Безопасность

- Приложение запускается от непривилегированного пользователя (UID 1000)
- Запрещено повышение привилегий
- Rate limiting для защиты API

## Структура chart

```
chart/
├── Chart.yaml           # Метаданные chart
├── values.yaml          # Значения по умолчанию
├── README.md            # Этот файл
├── item.yaml            # Конфигурация для TrueNAS catalog
├── questions/
│   └── questions.yaml   # Вопросы для интерфейса TrueNAS
└── templates/
    ├── deployment.yaml  # Kubernetes Deployment
    ├── service.yaml     # Kubernetes Service
    └── pvc.yaml         # PersistentVolumeClaim и PersistentVolume
```

## Поддержка

Для вопросов и проблем обращайтесь к документации или создайте issue в репозитории.

## Лицензия

[Укажите лицензию]
