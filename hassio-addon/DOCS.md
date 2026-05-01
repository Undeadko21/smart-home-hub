# Home Assistant Add-on: Smart Kiosk

Веб-приложение для умного дома с интеграцией Home Assistant и AI-ассистентом.

## Установка через HACS

1. Откройте Home Assistant
2. Перейдите в **HACS** → **Add-ons**
3. Найдите **Smart Kiosk** и установите
4. Запустите дополнение из панели **Настройки** → **Дополнения**

## Настройка

### Параметры конфигурации

```yaml
ha_url: ""              # URL Home Assistant (опционально)
ha_token: ""            # Long-Lived Access Token (опционально)
deepseek_key: ""        # API ключ DeepSeek (опционально)
```

### Получение токена Home Assistant

1. Откройте профиль пользователя в Home Assistant
2. Создайте **Long-Lived Access Token**
3. Скопируйте токен в настройку `ha_token`

## Поддержка

- GitHub: https://github.com/Undeadko21/smart-home-hub
- Issues: https://github.com/Undeadko21/smart-home-hub/issues
