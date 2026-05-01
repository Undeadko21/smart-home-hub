# Полная инструкция по установке Smart Kiosk

Эта инструкция описывает **единый универсальный способ** установки приложения Smart Kiosk на любом сервере или рабочей станции с поддержкой Docker.

---

## 📋 О приложении

Smart Kiosk — это веб-приложение для управления умным домом с интеграцией Home Assistant и AI-ассистентом на базе DeepSeek.

**Основные возможности:**
- Панель управления устройствами умного дома
- Интеграция с Home Assistant
- AI-ассистент на основе DeepSeek API
- Кэширование ответов для оптимизации
- Очередь уведомлений
- Защита от перегрузки (rate limiting)

---

## ✅ Требования

Перед установкой убедитесь, что у вас есть:

| Требование | Минимальная версия | Рекомендуемая версия |
|------------|-------------------|---------------------|
| **Операционная система** | Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+) | Ubuntu 22.04 LTS |
| **Docker** | 20.10+ | 24.0+ |
| **Docker Compose** | 2.0+ | 2.20+ |
| **CPU** | 1 ядро | 2 ядра |
| **RAM** | 512 МБ | 1 ГБ |
| **Диск** | 2 ГБ | 5 ГБ |
| **Порт** | 8080 (свободный) | Любой свободный |

### Проверка требований

```bash
# Проверить версию Docker
docker --version

# Проверить версию Docker Compose
docker compose version

# Проверить свободный порт 8080
sudo netstat -tlnp | grep :8080
# Или
sudo ss -tlnp | grep :8080
```

Если Docker не установлен — перейдите к [Приложению A](#приложение-а-установка-docker).

---

## 🚀 Быстрая установка (1 команда)

Для опытных пользователей — **полная установка одной командой**:

```bash
mkdir -p /opt/smart-kiosk && cd /opt/smart-kiosk && git clone https://github.com/Undeadko21/smart-home-hub.git . && cat > .env << 'EOF' && docker compose up -d --build
PORT=8080
DATA_PATH=/var/lib/smart-kiosk/data
HA_URL=
HA_TOKEN=
DEEPSEEK_KEY=
CPU_LIMIT=1.0
MEMORY_LIMIT=512M
RESTART_POLICY=unless-stopped
COMPOSE_PROJECT_NAME=smart-kiosk
DISABLE_HEALTHCHECK=false
LOG_DRIVER=json-file
MAX_LOG_SIZE=10m
MAX_LOG_FILES=3
EOF
```

Приложение будет доступно по адресу: `http://localhost:8080`

---

## 📖 Пошаговая инструкция

### Шаг 1: Подготовка директории

Создайте директорию для приложения и данных:

```bash
# Создайте основную директорию
sudo mkdir -p /opt/smart-kiosk
sudo mkdir -p /var/lib/smart-kiosk/data

# Установите права доступа
sudo chown -R $USER:$USER /opt/smart-kiosk
sudo chown -R $USER:$USER /var/lib/smart-kiosk/data

# Перейдите в директорию
cd /opt/smart-kiosk
```

> **Примечание:** Вы можете использовать другие пути, например `/home/user/apps/smart-kiosk`

---

### Шаг 2: Получение файлов приложения

#### Вариант А: Клонирование из Git (рекомендуется)

```bash
git clone https://github.com/Undeadko21/smart-home-hub.git .
```

#### Вариант Б: Ручное скачивание

1. Скачайте архив с GitHub: https://github.com/Undeadko21/smart-home-hub/archive/main.zip
2. Распакуйте в `/opt/smart-kiosk`
3. Убедитесь, что файлы `docker-compose.yaml` и `Dockerfile` находятся в корне

---

### Шаг 3: Настройка переменных окружения

Создайте файл `.env` в директории приложения:

```bash
nano .env
```

Вставьте следующее содержимое:

```ini
# ===== Основные настройки =====
# Имя проекта Docker Compose
COMPOSE_PROJECT_NAME=smart-kiosk

# Порт для доступа к веб-интерфейсу
PORT=8080

# Путь к данным на хосте (должен существовать!)
DATA_PATH=/var/lib/smart-kiosk/data

# Политика перезапуска контейнера
RESTART_POLICY=unless-stopped

# ===== Лимиты ресурсов =====
# Максимальное количество CPU ядер
CPU_LIMIT=1.0

# Максимальный объем памяти
MEMORY_LIMIT=512M

# ===== Home Assistant (опционально) =====
# URL вашего сервера Home Assistant
HA_URL=http://192.168.1.100:8123

# Long-Lived Access Token из Home Assistant
HA_TOKEN=your_home_assistant_token_here

# ===== AI настройки (опционально) =====
# API ключ DeepSeek для AI-ассистента
DEEPSEEK_KEY=your_deepseek_api_key_here

# ===== Дополнительные настройки =====
# Отключить проверку здоровья (true/false)
DISABLE_HEALTHCHECK=false

# Драйвер логирования
LOG_DRIVER=json-file

# Максимальный размер файла логов
MAX_LOG_SIZE=10m

# Количество файлов логов для ротации
MAX_LOG_FILES=3
```

#### Как получить токен Home Assistant:

1. Откройте Home Assistant в браузере
2. Нажмите на профиль пользователя (внизу слева)
3. Прокрутите вниз до раздела **"Long-Lived Access Tokens"**
4. Нажмите **"Create Token"**
5. Введите имя токена (например, `smart-kiosk`)
6. Скопируйте токен и вставьте в файл `.env`

> **Важно:** Токен показывается только один раз! Сохраните его в надёжном месте.

#### Как получить API ключ DeepSeek:

1. Зарегистрируйтесь на https://platform.deepseek.com/
2. Перейдите в раздел **API Keys**
3. Создайте новый ключ
4. Скопируйте и вставьте в файл `.env`

> **Примечание:** Без ключа DeepSeek AI-ассистент работать не будет, но остальные функции приложения останутся доступными.

Сохраните файл (Ctrl+O, Enter) и выйдите (Ctrl+X).

---

### Шаг 4: Создание Docker-образа и запуск

Соберите Docker-образ и запустите приложение одной командой:

```bash
docker compose up -d --build
```

Процесс сборки займёт 2-5 минут.

Вы увидите вывод:

```
[+] Running 2/2
 ✔ Network smart-kiosk_default    Created
 ✔ Container smart-kiosk        Started
```

---

### Шаг 5: Проверка установки

#### Проверка статуса контейнера

```bash
docker compose ps
```

Ожидаемый результат:

```
NAME            STATUS                    PORTS
smart-kiosk     Up (healthy)              0.0.0.0:8080->8080/tcp
```

Статус **healthy** означает, что проверка работоспособности прошла успешно.

#### Проверка логов

```bash
docker compose logs -f
```

Ожидаемые строки в логах:

```
INFO:     Uvicorn running on http://0.0.0.0:8080
INFO:     Application startup complete.
```

Нажмите `Ctrl+C` для выхода из режима просмотра логов.

#### Проверка работы приложения

Откройте браузер и перейдите по адресу:

```
http://<IP-адрес-сервера>:8080
```

Или локально:

```
http://localhost:8080
```

Вы должны увидеть веб-интерфейс Smart Kiosk.

#### Проверка API

```bash
curl http://localhost:8080/api/health
```

Ожидаемый ответ:

```json
{"status":"ok","timestamp":"2025-01-01T12:00:00"}
```

---

## 🔧 Управление приложением

### Просмотр статуса

```bash
docker compose ps
```

### Просмотр логов

```bash
# Логи в реальном времени
docker compose logs -f

# Последние 100 строк
docker compose logs --tail=100

# Логи с указанием времени
docker compose logs -f -t
```

### Остановка приложения

```bash
docker compose stop
```

### Запуск приложения

```bash
docker compose start
```

### Перезапуск приложения

```bash
docker compose restart
```

### Обновление приложения

```bash
# Перейдите в директорию приложения
cd /opt/smart-kiosk

# Обновите исходный код, пересоберите образ и пересоздайте контейнер
git pull origin main && docker compose up -d --build --force-recreate
```

### Полная остановка и удаление

```bash
# Остановить и удалить контейнеры (данные сохранятся)
docker compose down

# Полностью удалить включая сети (данные сохранятся)
docker compose down --remove-orphans

# Удалить всё, включая тома с данными (⚠️ данные будут удалены!)
docker compose down -v
```

---

## 🛡️ Безопасность

### Настройки безопасности по умолчанию

Приложение настроено со следующими мерами безопасности:

- ✅ Запуск от непривилегированного пользователя (UID 1000)
- ✅ Запрет повышения привилегий (`no-new-privileges`)
- ✅ Rate limiting для защиты от перегрузки API
- ✅ Проверка работоспособности (health check)

### Рекомендации по безопасности

1. **Используйте HTTPS:**
   - Настройте обратный прокси (Nginx, Traefik, Caddy)
   - Получите SSL-сертификат (Let's Encrypt)

2. **Защитите доступ к приложению:**
   - Используйте брандмауэр для ограничения доступа
   - Настройте аутентификацию на уровне прокси

3. **Регулярно обновляйте:**
   - Следите за обновлениями приложения
   - Обновляйте базовые образы Docker

4. **Храните секреты в безопасности:**
   - Не коммитьте файл `.env` в Git
   - Используйте защищённое хранилище для токенов

---

## 📊 Мониторинг

### Использование ресурсов

```bash
# Статистика использования CPU и памяти в реальном времени
docker stats smart-kiosk
```

### Проверка здоровья

```bash
# Быстрая проверка
curl -f http://localhost:8080/api/health

# Подробная информация о контейнере
docker inspect smart-kiosk | grep -A 20 Health
```

### Резервное копирование данных

Данные приложения хранятся в:
- `<DATA_PATH>/app.db` — база данных
- `<DATA_PATH>/logs/app.log` — логи приложения
- `<DATA_PATH>/cache/` — кэш AI-ответов

```bash
# Создание резервной копии
tar -czf smart-kiosk-backup-$(date +%Y%m%d-%H%M%S).tar.gz /var/lib/smart-kiosk/data

# Восстановление из резервной копии
tar -xzf smart-kiosk-backup-20250101-120000.tar.gz -C /var/lib/smart-kiosk/
```

---

## ❓ Решение проблем

### Проблема: Контейнер не запускается

**Шаг 1:** Проверьте логи

```bash
docker compose logs
```

**Шаг 2:** Проверьте, занят ли порт

```bash
sudo netstat -tlnp | grep :8080
```

Если порт занят, измените `PORT` в файле `.env`:

```ini
PORT=8081
```

Затем перезапустите:

```bash
docker compose down
docker compose up -d
```

**Шаг 3:** Проверьте права доступа к данным

```bash
ls -la /var/lib/smart-kiosk/data
sudo chmod 755 /var/lib/smart-kiosk/data
```

---

### Проблема: Ошибка подключения к Home Assistant

**Проверьте:**

1. Правильность URL в файле `.env`:
   ```ini
   HA_URL=http://192.168.1.100:8123
   ```

2. Доступность Home Assistant из сети сервера:
   ```bash
   curl http://192.168.1.100:8123
   ```

3. Правильность токена:
   - Токен должен быть Long-Lived Access Token
   - Токен не должен содержать лишних пробелов

4. Настройки firewall:
   ```bash
   sudo ufw allow from 192.168.1.0/24 to any port 8123
   ```

---

### Проблема: AI-ассистент не работает

**Проверьте:**

1. Наличие API ключа в `.env`:
   ```ini
   DEEPSEEK_KEY=sk-xxxxxxxxxxxxxxxx
   ```

2. Доступ в интернет из контейнера:
   ```bash
   docker exec smart-kiosk ping -c 3 api.deepseek.com
   ```

3. Лимиты API ключа:
   - Проверьте баланс на платформе DeepSeek
   - Убедитесь, что ключ активен

---

### Проблема: Приложение медленно работает

**Решения:**

1. Увеличьте лимиты ресурсов в `.env`:
   ```ini
   CPU_LIMIT=2.0
   MEMORY_LIMIT=1G
   ```

2. Перезапустите с новыми настройками:
   ```bash
   docker compose up -d
   ```

3. Проверьте использование ресурсов:
   ```bash
   docker stats smart-kiosk
   ```

---

### Проблема: Контейнер постоянно перезапускается

**Проверьте:**

1. Логи на наличие ошибок:
   ```bash
   docker compose logs --tail=50
   ```

2. Проверку здоровья:
   ```bash
   docker inspect smart-kiosk | grep -A 10 Health
   ```

3. Временно отключите health check в `.env`:
   ```ini
   DISABLE_HEALTHCHECK=true
   ```

---

## 📝 Переменные окружения

Полный список доступных переменных:

| Переменная | Описание | По умолчанию | Обязательная |
|------------|----------|--------------|--------------|
| `COMPOSE_PROJECT_NAME` | Имя проекта Docker | `smart-kiosk` | Нет |
| `PORT` | Порт для веб-интерфейса | `8080` | Нет |
| `DATA_PATH` | Путь к данным на хосте | `/mnt/data/smart-kiosk` | Нет |
| `RESTART_POLICY` | Политика перезапуска | `unless-stopped` | Нет |
| `CPU_LIMIT` | Лимит CPU ядер | `1.0` | Нет |
| `MEMORY_LIMIT` | Лимит памяти | `512M` | Нет |
| `HA_URL` | URL Home Assistant | `` | Нет |
| `HA_TOKEN` | Токен Home Assistant | `` | Нет |
| `DEEPSEEK_KEY` | API ключ DeepSeek | `` | Нет |
| `DISABLE_HEALTHCHECK` | Отключить health check | `false` | Нет |
| `LOG_DRIVER` | Драйвер логов | `json-file` | Нет |
| `MAX_LOG_SIZE` | Макс. размер логов | `10m` | Нет |
| `MAX_LOG_FILES` | Кол-во файлов логов | `3` | Нет |

---

## 🔗 Полезные ссылки

- [Документация Docker](https://docs.docker.com/)
- [Документация Docker Compose](https://docs.docker.com/compose/)
- [Документация Home Assistant](https://www.home-assistant.io/docs/)
- [DeepSeek API Documentation](https://platform.deepseek.com/docs)
- [GitHub репозиторий проекта](https://github.com/Undeadko21/smart-home-hub)

---

## 📞 Поддержка

Если вы столкнулись с проблемой, которой нет в этом руководстве:

1. Проверьте логи приложения
2. Изучите существующие Issues на GitHub
3. Создайте новый Issue с подробным описанием проблемы

---

## Приложение А: Установка Docker

### Для Ubuntu/Debian

```bash
# Обновите пакеты
sudo apt update

# Установите зависимости
sudo apt install -y ca-certificates curl gnupg lsb-release

# Добавьте GPG-ключ Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавьте репозиторий
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установите Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER

# Примените изменения группы (или перезайдите в систему)
newgrp docker

# Проверьте установку
docker --version
docker compose version
```

### Для CentOS/RHEL

```bash
# Установите зависимости
sudo yum install -y yum-utils

# Добавьте репозиторий
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Установите Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Запустите Docker
sudo systemctl start docker
sudo systemctl enable docker

# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER

# Примените изменения группы
newgrp docker

# Проверьте установку
docker --version
docker compose version
```

### Для других дистрибутивов

Следуйте официальной инструкции: https://docs.docker.com/engine/install/

---

## Приложение Б: Настройка обратного прокси (Nginx)

### Установка Nginx

```bash
sudo apt install -y nginx
```

### Конфигурация

Создайте файл конфигурации:

```bash
sudo nano /etc/nginx/sites-available/smart-kiosk
```

Вставьте содержимое:

```nginx
server {
    listen 80;
    server_name kiosk.yourdomain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Активируйте сайт:

```bash
sudo ln -s /etc/nginx/sites-available/smart-kiosk /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Настройка HTTPS с Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d kiosk.yourdomain.com
```

---

**Версия инструкции:** 1.0  
**Дата последнего обновления:** 2025  
**Совместимость:** Universal Docker (Linux, macOS, Windows WSL2)
