#!/bin/bash

# =============================================================================
# Скрипт установки/обновления приложения
# Поддерживает первичную установку и обновление существующей версии
# Все настройки выбираются интерактивно во время выполнения
# =============================================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Без цвета

# Конфигурация по умолчанию
APP_NAME="myapp"
APP_VERSION="1.0.0"
INSTALL_DIR="/opt/myapp"
CONFIG_DIR="/etc/myapp"
DATA_DIR="/var/lib/myapp"
CREATE_SHORTCUT=true
AUTO_START=false
LOG_LEVEL="info"
DOWNLOAD_URL=""

# Флаги
IS_UPDATE=false
VERBOSE=false

# =============================================================================
# Функции вывода
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =============================================================================
# Проверка прав доступа
# =============================================================================

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Этот скрипт должен выполняться от имени root"
        exit 1
    fi
}

# =============================================================================
# Определение состояния (установка или обновление)
# =============================================================================

check_existing_installation() {
    if [ -d "$INSTALL_DIR" ] && [ -f "$INSTALL_DIR/.installed" ]; then
        IS_UPDATE=true
        CURRENT_VERSION=$(cat "$INSTALL_DIR/.version" 2>/dev/null || echo "unknown")
        log_info "Обнаружена существующая установка версии: $CURRENT_VERSION"
        log_info "Будет выполнено обновление до версии: $APP_VERSION"
    else
        log_info "Выполняется первичная установка версии: $APP_VERSION"
    fi
}

# =============================================================================
# Интерактивный выбор настроек
# =============================================================================

configure_installation() {
    echo ""
    echo -e "${GREEN}=== Настройка установки ===${NC}"
    echo ""
    
    # Выбор каталога установки
    read -p "Каталог установки [$INSTALL_DIR]: " user_install_dir
    if [ -n "$user_install_dir" ]; then
        INSTALL_DIR="$user_install_dir"
    fi
    
    # Выбор каталога конфигурации
    read -p "Каталог конфигурации [$CONFIG_DIR]: " user_config_dir
    if [ -n "$user_config_dir" ]; then
        CONFIG_DIR="$user_config_dir"
    fi
    
    # Выбор каталога данных
    read -p "Каталог данных [$DATA_DIR]: " user_data_dir
    if [ -n "$user_data_dir" ]; then
        DATA_DIR="$user_data_dir"
    fi
    
    # Уровень логирования
    echo ""
    echo "Выберите уровень логирования:"
    echo "1) debug"
    echo "2) info (по умолчанию)"
    echo "3) warning"
    echo "4) error"
    read -p "Уровень логирования [2]: " log_choice
    case $log_choice in
        1) LOG_LEVEL="debug" ;;
        3) LOG_LEVEL="warning" ;;
        4) LOG_LEVEL="error" ;;
        *) LOG_LEVEL="info" ;;
    esac
    
    # Создание ярлыка
    echo ""
    read -p "Создать ярлык в меню приложений? (y/n) [y]: " shortcut_choice
    case $shortcut_choice in
        n|N) CREATE_SHORTCUT=false ;;
        *) CREATE_SHORTCUT=true ;;
    esac
    
    # Автозапуск
    echo ""
    read -p "Добавить в автозагрузку? (y/n) [n]: " autostart_choice
    case $autostart_choice in
        y|Y) AUTO_START=true ;;
        *) AUTO_START=false ;;
    esac
    
    # Дополнительные опции
    echo ""
    read -p "Включить подробный вывод (verbose)? (y/n) [n]: " verbose_choice
    case $verbose_choice in
        y|Y) VERBOSE=true ;;
        *) VERBOSE=false ;;
    esac
    
    echo ""
    log_info "Настройки сохранены:"
    echo "  - Каталог установки: $INSTALL_DIR"
    echo "  - Каталог конфигурации: $CONFIG_DIR"
    echo "  - Каталог данных: $DATA_DIR"
    echo "  - Уровень логирования: $LOG_LEVEL"
    echo "  - Создать ярлык: $CREATE_SHORTCUT"
    echo "  - Автозапуск: $AUTO_START"
    echo "  - Подробный вывод: $VERBOSE"
    echo ""
    
    read -p "Продолжить установку? (y/n) [y]: " confirm
    case $confirm in
        n|N) 
            log_warning "Установка отменена пользователем"
            exit 0
            ;;
    esac
}

# =============================================================================
# Подготовка окружения
# =============================================================================

prepare_environment() {
    log_info "Подготовка окружения..."
    
    # Создание каталогов
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$DATA_DIR"
    
    if [ "$VERBOSE" = true ]; then
        log_info "Созданы каталоги:"
        echo "  - $INSTALL_DIR"
        echo "  - $CONFIG_DIR"
        echo "  - $DATA_DIR"
    fi
}

# =============================================================================
# Загрузка приложения
# =============================================================================

download_application() {
    log_info "Загрузка приложения..."
    
    # Если URL не задан, используем заглушку
    # В реальном сценарии здесь будет скачивание из репозитория
    if [ -z "$DOWNLOAD_URL" ]; then
        log_warning "URL загрузки не указан, создаем демонстрационные файлы"
        
        # Создаем демонстрационный исполняемый файл
        cat > "$INSTALL_DIR/$APP_NAME" << 'EOF'
#!/bin/bash
echo "Приложение запущено!"
echo "Версия: 1.0.0"
echo "Логирование: info"
EOF
        chmod +x "$INSTALL_DIR/$APP_NAME"
    else
        # Скачивание архива
        TEMP_FILE=$(mktemp)
        curl -L -o "$TEMP_FILE" "$DOWNLOAD_URL"
        
        # Распаковка
        tar -xzf "$TEMP_FILE" -C "$INSTALL_DIR"
        rm -f "$TEMP_FILE"
    fi
    
    log_success "Приложение загружено"
}

# =============================================================================
# Настройка конфигурации
# =============================================================================

setup_configuration() {
    log_info "Настройка конфигурации..."
    
    # Создание файла конфигурации
    cat > "$CONFIG_DIR/config.conf" << EOF
# Конфигурационный файл $APP_NAME
# Сгенерировано: $(date)

[general]
app_name=$APP_NAME
version=$APP_VERSION
log_level=$LOG_LEVEL

[paths]
install_dir=$INSTALL_DIR
config_dir=$CONFIG_DIR
data_dir=$DATA_DIR

[features]
auto_start=$AUTO_START
verbose=$VERBOSE
EOF
    
    if [ "$IS_UPDATE" = true ] && [ -f "$CONFIG_DIR/config.conf.backup" ]; then
        log_info "Восстановление пользовательских настроек из резервной копии"
        # Здесь можно добавить логику слияния конфигов
    fi
    
    # Резервное копирование текущего конфига при обновлении
    if [ "$IS_UPDATE" = true ] && [ -f "$CONFIG_DIR/config.conf" ]; then
        cp "$CONFIG_DIR/config.conf" "$CONFIG_DIR/config.conf.backup.$(date +%Y%m%d%H%M%S)"
    fi
    
    log_success "Конфигурация создана"
}

# =============================================================================
# Создание ярлыка
# =============================================================================

create_shortcut() {
    if [ "$CREATE_SHORTCUT" = false ]; then
        log_info "Создание ярлыка пропущено"
        return
    fi
    
    log_info "Создание ярлыка в меню приложений..."
    
    cat > "/usr/share/applications/$APP_NAME.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Comment=$APP_NAME Application
Exec=$INSTALL_DIR/$APP_NAME
Icon=application-x-executable
Terminal=true
Categories=Utility;
EOF
    
    log_success "Ярлык создан"
}

# =============================================================================
# Настройка автозапуска
# =============================================================================

setup_autostart() {
    if [ "$AUTO_START" = false ]; then
        log_info "Автозапуск не настроен"
        return
    fi
    
    log_info "Настройка автозапуска..."
    
    # Для системных служб (systemd)
    cat > "/etc/systemd/system/$APP_NAME.service" << EOF
[Unit]
Description=$APP_NAME Service
After=network.target

[Service]
Type=simple
ExecStart=$INSTALL_DIR/$APP_NAME
Restart=on-failure
User=root
WorkingDirectory=$INSTALL_DIR

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable "$APP_NAME.service"
    
    log_success "Автозапуск настроен"
}

# =============================================================================
# Сохранение информации об установке
# =============================================================================

save_installation_info() {
    log_info "Сохранение информации об установке..."
    
    echo "$APP_VERSION" > "$INSTALL_DIR/.version"
    touch "$INSTALL_DIR/.installed"
    echo "$(date)" > "$INSTALL_DIR/.install_date"
    
    log_success "Информация об установке сохранена"
}

# =============================================================================
# Очистка старой версии (при обновлении)
# =============================================================================

cleanup_old_version() {
    if [ "$IS_UPDATE" = false ]; then
        return
    fi
    
    log_info "Очистка файлов старой версии..."
    # Удаляем только исполняемые файлы, сохраняя конфиги и данные
    find "$INSTALL_DIR" -type f -name "*.bin" -delete 2>/dev/null || true
    find "$INSTALL_DIR" -type f -name "*.so" -delete 2>/dev/null || true
    
    log_success "Старая версия очищена"
}

# =============================================================================
# Завершение установки
# =============================================================================

finalize_installation() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    if [ "$IS_UPDATE" = true ]; then
        echo -e "${GREEN}Обновление завершено успешно!${NC}"
        echo "Версия: $CURRENT_VERSION -> $APP_VERSION"
    else
        echo -e "${GREEN}Установка завершена успешно!${NC}"
        echo "Версия: $APP_VERSION"
    fi
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Каталог установки: $INSTALL_DIR"
    echo "Конфигурация: $CONFIG_DIR/config.conf"
    echo "Данные: $DATA_DIR"
    echo ""
    
    if [ "$AUTO_START" = true ]; then
        echo "Сервис запущен и добавлен в автозагрузку"
        systemctl start "$APP_NAME.service"
    fi
    
    echo ""
    log_info "Для запуска приложения выполните: $INSTALL_DIR/$APP_NAME"
    echo ""
}

# =============================================================================
# Основная функция
# =============================================================================

main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Скрипт установки/обновления $APP_NAME${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    
    # Проверка прав
    check_root
    
    # Определение состояния
    check_existing_installation
    
    # Интерактивная настройка
    configure_installation
    
    # Подготовка
    prepare_environment
    
    # Очистка при обновлении
    cleanup_old_version
    
    # Загрузка
    download_application
    
    # Конфигурация
    setup_configuration
    
    # Ярлык
    create_shortcut
    
    # Автозапуск
    setup_autostart
    
    # Сохранение информации
    save_installation_info
    
    # Завершение
    finalize_installation
}

# =============================================================================
# ИНСТРУКЦИЯ ПО ЗАПУСКУ
# =============================================================================
# 
# 1. Сделайте скрипт исполняемым:
#    chmod +x install_app.sh
#
# 2. Запустите скрипт от имени root:
#    sudo ./install_app.sh
#    или
#    su -c './install_app.sh'
#
# 3. Во время выполнения вам будет предложено:
#    - Выбрать каталог установки (по умолчанию /opt/myapp)
#    - Выбрать каталог конфигурации (по умолчанию /etc/myapp)
#    - Выбрать каталог данных (по умолчанию /var/lib/myapp)
#    - Выбрать уровень логирования (debug/info/warning/error)
#    - Решить, создавать ли ярлык в меню приложений
#    - Решить, добавлять ли приложение в автозагрузку
#    - Включить ли подробный вывод (verbose режим)
#
# 4. При повторном запуске скрипт автоматически определит существующую
#    установку и выполнит обновление с сохранением настроек.
#
# ПРИМЕЧАНИЕ: Перед использованием установите переменную DOWNLOAD_URL
#             с актуальным URL для загрузки приложения.
# =============================================================================

# Запуск основной функции
main "$@"
