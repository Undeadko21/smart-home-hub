# Smart Kiosk - Helm Chart для TrueNAS SCALE 25.10.1 Goldeye

Приложение Smart Kiosk для установки через веб-интерфейс TrueNAS SCALE с использованием Helm chart.

## Структура

```
chart/
├── Chart.yaml           # Метаданные chart 
├── values.yaml          # Значения по умолчанию
├── item.yaml            # Конфигурация для каталога TrueNAS
├── questions/
│   └── questions.yaml   # Вопросы для интерфейса установки TrueNAS
└── templates/
    ├── deployment.yaml  # Kubernetes Deployment
    ├── service.yaml     # Kubernetes Service
    └── pvc.yaml         # PersistentVolumeClaim
```

## Установка на TrueNAS SCALE 25.10.1 Goldeye

### Через веб-интерфейс (рекомендуется)

1. Откройте **Apps** → **Manage Catalogs** в интерфейсе TrueNAS
2. Добавьте новый каталог:
   - **Name**: `smart-kiosk`
   - **Repository URL**: `https://github.com/Undeadko21/smart-home-hub.git`
   - **Branch**: `main`
3. Нажмите **Save**
4. Перейдите в **Apps** → **Discover Apps**
5. Найдите **Smart Kiosk** и нажмите **Install**
6. Настройте параметры через веб-форму:
   - Порт приложения (по умолчанию 8080)
   - Путь хранения данных (по умолчанию `/mnt/data/smart-kiosk`)
   - Home Assistant URL и токен (опционально)
   - DeepSeek API ключ (опционально)
   - Лимиты CPU и памяти
7. Нажмите **Install**

После установки приложение будет доступно по адресу: `http://<IP-TruNAS>:8080`

### Все настройки через веб-интерфейс

После установки все параметры можно изменить через веб-интерфейс приложения:
- Токены Home Assistant
- API ключи AI сервисов
- Сетевые настройки
- Лимиты ресурсов

Для этого перейдите в **Apps** → **Installed Apps** → **Smart Kiosk** → **Edit**.

## Управление

```bash
# Проверка статуса (через kubectl на TrueNAS)
kubectl get pods -n ix-smart-kiosk

# Просмотр логов
kubectl logs -n ix-smart-kiosk -l app.kubernetes.io/name=smart-kiosk -f

# Удаление приложения
helm uninstall smart-kiosk -n ix-smart-kiosk
```

Или используйте веб-интерфейс TrueNAS: **Apps** → **Installed Apps** → **Smart Kiosk** → три точки → **Delete**.

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| `DATA_DIR` | Директория данных (`/app/data`) |
| `HA_URL` | Home Assistant URL |
| `HA_TOKEN` | Home Assistant Long-Lived Access Token |
| `DEEPSEEK_KEY` | DeepSeek API Key |

## Требования

- TrueNAS SCALE 25.10.1 Goldeye или новее
- Kubernetes >= 1.25.0
- Helm 3.x
