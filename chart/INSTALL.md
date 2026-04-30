# Smart Kiosk - Установка из GitHub через YAML интерфейс

Приложение Smart Kiosk для TrueNAS SCALE с установкой напрямую из GitHub репозитория.

## Структура

```
chart/
├── Chart.yaml           # Метаданные chart с GitHub конфигурацией
├── values.yaml          # Значения по умолчанию
├── README.md            # Документация для пользователей
├── item.yaml            # Конфигурация для каталога TrueNAS с git_repo
├── questions/
│   └── questions.yaml   # Вопросы для интерфейса установки
└── templates/
    ├── deployment.yaml  # Kubernetes Deployment
    ├── service.yaml     # Kubernetes Service
    └── pvc.yaml         # PersistentVolumeClaim и PersistentVolume
```

## Установка из GitHub через YAML интерфейс (рекомендуется)

### Вариант 1: Через веб-интерфейс TrueNAS SCALE

1. Откройте **Apps** → **Manage Catalogs** в интерфейсе TrueNAS
2. Добавьте новый каталог:
   - **Name**: `smart-kiosk`
   - **Repository URL**: `https://github.com/YOUR_USERNAME/smart-kiosk.git`
   - **Branch**: `main`
3. Нажмите **Save** для добавления каталога
4. Перейдите в **Apps** → **Discover Apps**
5. Найдите **Smart Kiosk** и нажмите **Install**
6. Настройте параметры через веб-форму
7. Нажмите **Install**

### Вариант 2: Установка через YAML файл

Создайте файл `smart-kiosk-values.yaml` с вашими настройками:

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

Затем установите приложение через CLI:

```bash
# Клонировать репозиторий
git clone https://github.com/YOUR_USERNAME/smart-kiosk.git
cd smart-kiosk

# Установить приложение с вашими значениями
helm install smart-kiosk ./chart \
  --namespace ix-smart-kiosk \
  --create-namespace \
  -f smart-kiosk-values.yaml
```

### Вариант 3: Прямая установка из GitHub

```bash
# Установка напрямую из GitHub репозитория
helm install smart-kiosk \
  oci://ghcr.io/YOUR_USERNAME/smart-kiosk-chart \
  --namespace ix-smart-kiosk \
  --create-namespace
```

Или используя git как источник:

```bash
# Добавить Helm репозиторий из GitHub
helm repo add smart-kiosk https://YOUR_USERNAME.github.io/smart-kiosk

# Обновить репозиторий
helm repo update

# Установить приложение
helm install smart-kiosk smart-kiosk/smart-kiosk \
  --namespace ix-smart-kiosk \
  --create-namespace
```

## Обновление версии

Для обновления версии приложения:

1. Измените версию в `Chart.yaml`:
   ```yaml
   version: 1.0.1  # увеличьте версию
   appVersion: "1.0.1"
   ```

2. В TrueNAS SCALE:
   - Перейдите в **Apps** → **Installed Apps**
   - Выберите **Smart Kiosk**
   - Нажмите **Update** если доступна новая версия

## Добавление в каталог TrueNAS

Для добавления приложения в официальный или community каталог:

1. Создайте репозиторий с chart
2. Добавьте URL репозитория в настройки TrueNAS (**Apps** → **Manage Catalogs**)
3. Приложение появится в разделе **Discover Apps**

Формат репозитория должен соответствовать требованиям TrueNAS SCALE:
- `item.yaml` с категориями
- `questions/questions.yaml` с формой настройки
- `templates/` с Kubernetes манифестами

## Тестирование локально

```bash
# Проверка шаблона
helm template test-release ./chart

# Установка в локальный Kubernetes
helm install test-release ./chart --namespace test --create-namespace

# Проверка статуса
helm status test-release -n test

# Удаление
helm uninstall test-release -n test
```

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `DATA_DIR` | Директория данных | `/app/data` |
| `HA_URL` | Home Assistant URL | `` |
| `HA_TOKEN` | Home Assistant токен | `` |
| `DEEPSEEK_KEY` | DeepSeek API ключ | `` |

## Поддержка

- Версия TrueNAS SCALE: 22.02+
- Kubernetes: встроенный в TrueNAS

## Лицензия

[Укажите лицензию]
