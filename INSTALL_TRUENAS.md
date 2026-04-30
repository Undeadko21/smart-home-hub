# Установка Smart Kiosk на TrueNAS SCALE

Это руководство описывает, как установить приложение Smart Kiosk на TrueNAS SCALE через интерфейс Apps.

## Предварительные требования

- TrueNAS SCALE версии 22.02 или новее
- Настроенный каталог приложений (Apps)
- Доступ в интернет (для загрузки образа и работы AI)

## Структура проекта

```
/workspace/
├── chart/                    # Helm chart для TrueNAS
│   ├── Chart.yaml           # Метаданные приложения
│   ├── values.yaml          # Значения по умолчанию
│   ├── item.yaml            # Конфигурация для каталога
│   ├── README.md            # Документация для пользователей
│   ├── INSTALL.md           # Техническая документация
│   ├── questions/
│   │   └── questions.yaml   # Форма настройки в интерфейсе
│   └── templates/
│       ├── deployment.yaml  # Kubernetes Deployment
│       ├── service.yaml     # Kubernetes Service
│       └── pvc.yaml         # PersistentVolume
├── Dockerfile               # Docker образ приложения
├── docker-compose.yaml      # Локальная разработка
└── backend/                 # Исходный код приложения
```

## Способ 1: Добавление в локальный каталог (рекомендуется для разработки)

### Шаг 1: Подготовка директории

1. Создайте директорию для каталога приложений:
```bash
mkdir -p /mnt/data/catalogs/my-catalog/community/smart-kiosk
```

2. Скопируйте chart в каталог:
```bash
cp -r /workspace/chart/* /mnt/data/catalogs/my-catalog/community/smart-kiosk/
```

### Шаг 2: Добавление каталога в TrueNAS

1. Откройте веб-интерфейс TrueNAS
2. Перейдите в **Apps** → **Manage Catalogs**
3. Нажмите **Add Catalog**
4. Заполните:
   - **Catalog Name**: `my-catalog`
   - **Repository URL**: Путь к локальной директории или Git репозиторию
   - **Branch**: `master` или `main`
   - **Location**: `/mnt/data/catalogs/my-catalog`
5. Нажмите **Save**

### Шаг 3: Установка приложения

1. Перейдите в **Apps** → **Discover Apps**
2. Найдите **Smart Kiosk** в каталоге
3. Нажмите **Install**
4. Настройте параметры:
   - **Port**: 8080 (или другой свободный порт)
   - **Data Storage Path**: `/mnt/data/smart-kiosk`
   - **Home Assistant URL**: (опционально) адрес вашего HA
   - **Home Assistant Token**: (опционально) токен доступа
   - **DeepSeek API Key**: (опционально) ключ AI
5. Нажмите **Install**

## Способ 2: Установка через Git репозиторий

### Шаг 1: Публикация chart

1. Создайте Git репозиторий (GitHub, GitLab, etc.)
2. Разместите содержимое директории `chart/` в репозитории
3. Убедитесь, что структура соответствует требованиям TrueNAS

### Шаг 2: Добавление в TrueNAS

1. **Apps** → **Manage Catalogs** → **Add Catalog**
2. Укажите URL вашего Git репозитория
3. После синхронизации приложение появится в **Discover Apps**

## Обновление приложения

### Через интерфейс TrueNAS

1. Перейдите в **Apps** → **Installed Apps**
2. Выберите **Smart Kiosk**
3. Если доступна новая версия, нажмите **Update**
4. Подтвердите обновление

Все данные сохраняются при обновлении благодаря PersistentVolume.

### Ручное обновление версии

1. Измените версию в `chart/Chart.yaml`:
```yaml
version: 1.0.1  # увеличьте версию
appVersion: "1.0.1"
```

2. Закоммитьте изменения в Git (если используете репозиторий)
3. В TrueNAS обновите каталог: **Apps** → **Manage Catalogs** → **Sync All**
4. Обновите приложение

## Мониторинг и логи

### Просмотр логов

1. **Apps** → **Installed Apps** → **Smart Kiosk**
2. Перейдите на вкладку **Logs**
3. Или через CLI:
```bash
kubectl logs -n ix-smart-kiosk deploy/smart-kiosk-kiosk
```

### Проверка состояния

1. **Apps** → **Installed Apps** → **Smart Kiosk**
2. Проверьте статус на вкладке **Details**
3. Health check endpoint: `http://<IP>:<port>/api/health`

## Управление данными

Данные приложения хранятся в:
- `<DATA_PATH>/app.db` — база данных
- `<DATA_PATH>/logs/app.log` — логи
- `<DATA_PATH>/cache/` — кэш AI ответов

Для резервного копирования скопируйте директорию данных.

## Удаление приложения

1. **Apps** → **Installed Apps** → **Smart Kiosk**
2. Нажмите **Delete**
3. Подтвердите удаление

**Важно**: Данные сохраняются на хосте. Для полного удаления удалите директорию данных вручную.

## Решение проблем

### Приложение не запускается

1. Проверьте логи в интерфейсе TrueNAS
2. Убедитесь, что порт не занят
3. Проверьте права доступа к директории данных

### Ошибки подключения к Home Assistant

1. Проверьте правильность URL и токена
2. Убедитесь, что Home Assistant доступен из сети TrueNAS
3. Проверьте firewall правила

### AI не работает

1. Проверьте наличие API ключа DeepSeek
2. Убедитесь в наличии доступа в интернет
3. Проверьте лимиты API ключа

## Дополнительная информация

- [Документация TrueNAS SCALE Apps](https://www.truenas.com/docs/scale/scaleapps/)
- [Helm Chart Documentation](https://helm.sh/docs/)
