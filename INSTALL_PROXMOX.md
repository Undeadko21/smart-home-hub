# Установка Smart Kiosk на Proxmox

Это руководство описывает установку приложения Smart Kiosk на Proxmox VE с использованием Docker Compose в LXC контейнере или виртуальной машине.

## Предварительные требования

- Proxmox VE 7.x или новее
- LXC контейнер (Debian 11/12, Ubuntu 20.04/22.04) или VM с Linux
- Docker и Docker Compose установленные внутри контейнера/VM
- Доступ в интернет для загрузки образов и работы AI
- Свободный порт для доступа к приложению (по умолчанию 8080)

## Структура проекта

```
/workspace/
├── Dockerfile               # Docker образ приложения
├── docker-compose.yaml      # Конфигурация Docker Compose
├── backend/                 # Исходный код приложения
└── static/                  # Веб-интерфейс
```

---

## Вариант 1: Установка в LXC контейнере (рекомендуется)

### Шаг 1: Создание LXC контейнера

1. Откройте веб-интерфейс Proxmox
2. Нажмите **Create CT** (верхний правый угол)
3. Настройте контейнер:

   **General:**
   - Node: выберите ваш узел
   - CT ID: автоматически или укажите вручную (например, 100)
   - Hostname: `smart-kiosk`

   **Template:**
   - Выберите образ: `debian-12-standard` или `ubuntu-22.04-standard`
   - Если шаблонов нет, скачайте их в **PVE → local (pve) → CT Templates → Templates**

   **Disk:**
   - Disk size: `8 GB` (минимум)
   - Storage: выберите ваше хранилище

   **CPU:**
   - Cores: `2`
   - CPU units: `1024`

   **Memory:**
   - Memory: `1024 MB`
   - Swap: `512 MB`

   **Network:**
   - IPv4: DHCP или статический адрес
   - IPv6: по необходимости

   **Confirm:**
   - Проверьте настройки и нажмите **Finish**

4. После создания контейнера, включите опции для Docker:

   ```bash
   # В хосте Proxmox выполните:
   pct set 100 -features nesting=1,keyctl=1
   pct set 100 -lxc.cgroup2.devices.allow: a
   pct set 100 -lxc.cap.drop:
   ```

   Где `100` - ID вашего контейнера.

### Шаг 2: Подключение к контейнеру и установка Docker

```bash
# Подключитесь к консоли контейнера из Proxmox
pct enter 100

# Или по SSH
ssh root@<IP-контейнера>
```

#### Для Debian 12:

```bash
# Обновите пакеты
apt update && apt upgrade -y

# Установите зависимости
apt install -y ca-certificates curl gnupg

# Добавьте GPG-ключ Docker
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Добавьте репозиторий
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установите Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Добавьте пользователя в группу docker
usermod -aG docker $USER

# Проверьте установку
docker --version
docker compose version
```

#### Для Ubuntu 22.04:

```bash
# Обновите пакеты
apt update && apt upgrade -y

# Установите зависимости
apt install -y ca-certificates curl gnupg lsb-release

# Добавьте GPG-ключ Docker
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Добавьте репозиторий
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установите Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Добавьте пользователя в группу docker
usermod -aG docker $USER

# Проверьте установку
docker --version
docker compose version
```

### Шаг 3: Подготовка директории для приложения

```bash
# Создайте директорию для приложения
mkdir -p /opt/smart-kiosk
mkdir -p /var/lib/smart-kiosk/data

# Установите права доступа
chown -R $USER:$USER /opt/smart-kiosk
chown -R $USER:$USER /var/lib/smart-kiosk/data

# Перейдите в директорию приложения
cd /opt/smart-kiosk
```

### Шаг 4: Клонирование репозитория

```bash
# Клонируйте репозиторий
git clone https://github.com/Undeadko21/smart-home-hub.git .
```

Или скопируйте файлы вручную, если нет доступа к Git.

### Шаг 5: Настройка переменных окружения

Создайте файл `.env`:

```bash
nano .env
```

Вставьте содержимое:

```ini
# ===== Основные настройки =====
COMPOSE_PROJECT_NAME=smart-kiosk
PORT=8080
DATA_PATH=/var/lib/smart-kiosk/data
RESTART_POLICY=unless-stopped

# ===== Лимиты ресурсов =====
CPU_LIMIT=1.0
MEMORY_LIMIT=512M

# ===== Home Assistant (опционально) =====
HA_URL=http://192.168.1.100:8123
HA_TOKEN=your_home_assistant_token_here

# ===== AI настройки (опционально) =====
DEEPSEEK_KEY=your_deepseek_api_key_here

# ===== Дополнительные настройки =====
DISABLE_HEALTHCHECK=false
LOG_DRIVER=json-file
MAX_LOG_SIZE=10m
MAX_LOG_FILES=3
```

Сохраните файл (Ctrl+O, Enter) и выйдите (Ctrl+X).

### Шаг 6: Создание Docker-образа

```bash
# Соберите Docker-образ
docker build -t smart-kiosk:latest .
```

Процесс сборки займёт 2-5 минут.

### Шаг 7: Запуск приложения

```bash
# Запустите приложение в фоновом режиме
docker compose up -d
```

### Шаг 8: Проверка установки

```bash
# Проверьте статус контейнера
docker compose ps

# Просмотрите логи
docker compose logs -f

# Проверьте работу API
curl http://localhost:8080/api/health
```

Откройте браузер и перейдите по адресу: `http://<IP-контейнера>:8080`

---

## Вариант 2: Установка в виртуальной машине (VM)

### Шаг 1: Создание VM

1. Откройте веб-интерфейс Proxmox
2. Нажмите **Create VM**
3. Настройте виртуальную машину:

   **General:**
   - Node: выберите ваш узел
   - VM ID: автоматически или вручную (например, 100)
   - Name: `smart-kiosk-vm`

   **OS:**
   - Выберите ISO образ (Debian 12, Ubuntu 22.04, etc.)
   - Если нет образов, загрузите их в **PVE → local (pve) → ISO Images**

   **System:**
   - Graphical display: отключите (если не нужен GUI)
   - QEMU Agent: включите

   **Disks:**
   - Bus/Device: VirtIO Block
   - Storage: выберите ваше хранилище
   - Disk size: `20 GB`

   **CPU:**
   - Category: host
   - Cores: `2`
   - Type: x86-64-v2-AES

   **Memory:**
   - Memory: `2048 MB`
   - Ballooning Device: отключите

   **Network:**
   - Model: VirtIO (paravirtualized)
   - Bridge: vmbr0

   **Confirm:**
   - Проверьте настройки и нажмите **Finish**

4. Установите операционную систему через консоль VM

### Шаг 2: Установка Docker в VM

После установки ОС, выполните шаги из **Варианта 1, Шаг 2** для установки Docker.

### Шаг 3: Установка приложения

Выполните шаги из **Варианта 1, Шаги 3-8** для установки приложения.

---

## Вариант 3: Установка через cloud-init (для продвинутых пользователей)

Для автоматизации развертывания можно использовать cloud-init:

### Шаг 1: Подготовка cloud-config

Создайте файл `cloud-config.yaml`:

```yaml
#cloud-config
hostname: smart-kiosk
manage_etc_hosts: true

packages:
  - docker.io
  - docker-compose
  - git

users:
  - name: admin
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: docker
    shell: /bin/bash
    ssh_authorized_keys:
      - ssh-rsa AAAA... ваш_публичный_ключ

runcmd:
  - systemctl enable docker
  - systemctl start docker
  - mkdir -p /opt/smart-kiosk
  - mkdir -p /var/lib/smart-kiosk/data
  - cd /opt/smart-kiosk
  - git clone https://github.com/Undeadko21/smart-home-hub.git .
  - |
    cat > /opt/smart-kiosk/.env << EOF
    COMPOSE_PROJECT_NAME=smart-kiosk
    PORT=8080
    DATA_PATH=/var/lib/smart-kiosk/data
    RESTART_POLICY=unless-stopped
    CPU_LIMIT=1.0
    MEMORY_LIMIT=512M
    HA_URL=
    HA_TOKEN=
    DEEPSEEK_KEY=
    DISABLE_HEALTHCHECK=false
    LOG_DRIVER=json-file
    MAX_LOG_SIZE=10m
    MAX_LOG_FILES=3
    EOF
  - cd /opt/smart-kiosk && docker build -t smart-kiosk:latest .
  - cd /opt/smart-kiosk && docker compose up -d

final_message: "Smart Kiosk успешно установлен и запущен!"
```

### Шаг 2: Создание VM с cloud-init

1. Создайте VM как обычно
2. В разделе **Cloud-init** укажите:
   - User: `admin`
   - Password: (или используйте SSH ключи)
   - DNS domain: ваш домен
   - DNS servers: 8.8.8.8, 1.1.1.1
3. Загрузите `cloud-config.yaml` как user-data

---

## Управление приложением

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

# Обновите исходный код из Git
git pull origin main

# Пересоберите образ
docker build -t smart-kiosk:latest .

# Пересоздайте контейнер
docker compose up -d --force-recreate
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

## Мониторинг

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

## Решение проблем

### Контейнер не запускается

**Шаг 1:** Проверьте логи

```bash
docker compose logs
```

**Шаг 2:** Проверьте, занят ли порт

```bash
netstat -tlnp | grep :8080
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
chmod 755 /var/lib/smart-kiosk/data
```

### Ошибка подключения к Home Assistant

**Проверьте:**

1. Правильность URL в файле `.env`:
   ```ini
   HA_URL=http://192.168.1.100:8123
   ```

2. Доступность Home Assistant из сети контейнера:
   ```bash
   curl http://192.168.1.100:8123
   ```

3. Правильность токена:
   - Токен должен быть Long-Lived Access Token
   - Токен не должен содержать лишних пробелов

4. Настройки firewall:
   ```bash
   ufw allow from 192.168.1.0/24 to any port 8123
   ```

### AI-ассистент не работает

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

### Приложение медленно работает

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

### Контейнер постоянно перезапускается

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

## Переменные окружения

Полный список доступных переменных:

| Переменная | Описание | По умолчанию | Обязательная |
|------------|----------|--------------|--------------|
| `COMPOSE_PROJECT_NAME` | Имя проекта Docker | `smart-kiosk` | Нет |
| `PORT` | Порт для веб-интерфейса | `8080` | Нет |
| `DATA_PATH` | Путь к данным на хосте | `/var/lib/smart-kiosk/data` | Нет |
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

## Настройка сетевого моста в Proxmox

Для доступа к приложению из внешней сети убедитесь, что сетевой мост настроен правильно:

1. Откройте **PVE → System → Network**
2. Проверьте наличие `vmbr0` (Linux Bridge)
3. Если моста нет, создайте его:
   - Type: Linux Bridge
   - Name: `vmbr0`
   - Bridge ports: ваш физический интерфейс (например, `enp1s0`)
   - CIDR: IP-адрес и маска (например, `192.168.1.10/24`)
   - Gateway: шлюз по умолчанию

---

## Безопасность

### Рекомендации по безопасности для Proxmox

1. **Изоляция контейнера:**
   - Используйте отдельный LXC контейнер для приложения
   - Ограничьте ресурсы контейнера

2. **Настройки брандмауэра Proxmox:**
   ```bash
   # В хосте Proxmox настройте firewall
   pvesh create /nodes/<node>/firewall/rules \
     --action ACCEPT \
     --dest <IP-контейнера> \
     --dport 8080 \
     --proto tcp \
     --source 192.168.1.0/24
   ```

3. **Безопасность внутри контейнера:**
   - Не запускайте процессы от root внутри контейнера
   - Регулярно обновляйте пакеты
   - Используйте HTTPS через обратный прокси

4. **Резервное копирование:**
   - Настройте регулярное резервное копирование контейнера в Proxmox
   - Используйте встроенные средства Proxmox Backup Server

---

## Полезные ссылки

- [Документация Proxmox VE](https://pve.proxmox.com/wiki/Main_Page)
- [Документация Docker](https://docs.docker.com/)
- [Документация Docker Compose](https://docs.docker.com/compose/)
- [Документация Home Assistant](https://www.home-assistant.io/docs/)
- [DeepSeek API Documentation](https://platform.deepseek.com/docs)
- [GitHub репозиторий проекта](https://github.com/Undeadko21/smart-home-hub)

---

## Поддержка

Если вы столкнулись с проблемой:

1. Проверьте логи приложения
2. Изучите документацию Proxmox и Docker
3. Создайте Issue на GitHub с подробным описанием проблемы

---

**Версия инструкции:** 1.0  
**Дата последнего обновления:** 2025  
**Совместимость:** Proxmox VE 7.x+, Debian 11/12, Ubuntu 20.04/22.04
