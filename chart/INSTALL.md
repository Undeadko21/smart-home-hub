# Smart Kiosk - Helm Chart для TrueNAS SCALE

Это директория содержит Helm chart для установки приложения Smart Kiosk на TrueNAS SCALE.

## Структура

```
chart/
├── Chart.yaml           # Метаданные chart
├── values.yaml          # Значения по умолчанию
├── README.md            # Документация для пользователей
├── item.yaml            # Конфигурация для каталога TrueNAS
├── questions/
│   └── questions.yaml   # Вопросы для интерфейса установки
└── templates/
    ├── deployment.yaml  # Kubernetes Deployment
    ├── service.yaml     # Kubernetes Service
    └── pvc.yaml         # PersistentVolumeClaim и PersistentVolume
```

## Установка на TrueNAS SCALE

### Вариант 1: Через веб-интерфейс (рекомендуется)

1. Скопируйте директорию `chart` в каталог приложений TrueNAS
2. В интерфейсе TrueNAS перейдите в **Apps** → **Discover Apps**
3. Найдите **Smart Kiosk** и нажмите **Install**
4. Настройте параметры через веб-форму
5. Нажмите **Install**

### Вариант 2: Через CLI

```bash
# Добавить каталог с chart
helm repo add smart-kiosk /path/to/chart

# Установить приложение
helm install smart-kiosk ./chart --namespace ix-smart-kiosk --create-namespace
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
