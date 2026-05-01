# Smart Kiosk - Helm Chart для Kubernetes/TrueNAS SCALE

Приложение Smart Kiosk для Kubernetes и TrueNAS SCALE с установкой через Helm.

## Структура

```
chart/
├── Chart.yaml           # Метаданные chart 
├── values.yaml          # Значения по умолчанию
├── README.md            # Документация для пользователей
├── item.yaml            # Конфигурация для каталога TrueNAS
├── questions/
│   └── questions.yaml   # Вопросы для интерфейса установки TrueNAS
└── templates/
    ├── deployment.yaml  # Kubernetes Deployment
    ├── service.yaml     # Kubernetes Service
    └── pvc.yaml         # PersistentVolumeClaim и PersistentVolume
```

## Установка на Kubernetes

### Вариант 1: Через Helm CLI

```bash
# Клонировать репозиторий
git clone https://github.com/Undeadko21/smart-home-hub.git
cd smart-home-hub/chart

# Установить приложение
helm install smart-kiosk . \
  --namespace ix-smart-kiosk \
  --create-namespace
```

### Вариант 2: С кастомными значениями

Создайте файл `custom-values.yaml`:

```yaml
ha_url: "http://192.168.1.100:8123"
ha_token: "your_long_lived_token"
deepseek_key: "your_deepseek_api_key"

service:
  type: LoadBalancer
  port: 8080

storage:
  hostPath: "/mnt/data/smart-kiosk"
```

Установите с кастомными значениями:

```bash
helm install smart-kiosk . -f custom-values.yaml --namespace ix-smart-kiosk --create-namespace
```

## Установка на TrueNAS SCALE

### Вариант 1: Через веб-интерфейс TrueNAS SCALE

1. Откройте **Apps** → **Manage Catalogs** в интерфейсе TrueNAS
2. Добавьте новый каталог:
   - **Name**: `smart-kiosk`
   - **Repository URL**: `https://github.com/Undeadko21/smart-home-hub.git`
   - **Branch**: `main`
3. Нажмите **Save** для добавления каталога
4. Перейдите в **Apps** → **Discover Apps**
5. Найдите **Smart Kiosk** и нажмите **Install**
6. Настройте параметры через веб-форму
7. Нажмите **Install**

### Вариант 2: Через Helm CLI на TrueNAS

```bash
# Клонировать репозиторий
git clone https://github.com/Undeadko21/smart-home-hub.git
cd smart-home-hub/chart

# Создать файл значений
cat > values-custom.yaml << EOF
ha_url: "http://192.168.1.100:8123"
ha_token: "your_token"
deepseek_key: "your_api_key"
EOF

# Установить приложение
helm install smart-kiosk . \
  --namespace ix-smart-kiosk \
  --create-namespace \
  -f values-custom.yaml
```

## Обновление версии

Для обновления версии приложения:

```bash
# Перейдите в директорию chart
cd smart-home-hub/chart

# Обновите код из репозитория
git pull

# Обновите релиз
helm upgrade smart-kiosk . --namespace ix-smart-kiosk
```

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `DATA_DIR` | Директория данных | `/app/data` |
| `HA_URL` | Home Assistant URL | `` |
| `HA_TOKEN` | Home Assistant токен | `` |
| `DEEPSEEK_KEY` | DeepSeek API ключ | `` |

## Управление релизом

```bash
# Проверка статуса
helm status smart-kiosk -n ix-smart-kiosk

# Просмотр логов
kubectl logs -n ix-smart-kiosk -l app.kubernetes.io/name=smart-kiosk -f

# Масштабирование (не рекомендуется, приложение stateful)
helm upgrade smart-kiosk . --set replicaCount=2 -n ix-smart-kiosk

# Удаление
helm uninstall smart-kiosk -n ix-smart-kiosk
```

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

## Поддержка

- Версия Kubernetes: >= 1.25.0
- Версия Helm: 3.x
- Версия TrueNAS SCALE: 22.02+

## Лицензия

[Укажите лицензию]
