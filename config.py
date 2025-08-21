# -*- coding: utf-8 -*-
# @Аутор    : minciv
# @Фајл     : config.py
# @Верзија  : 0.2.0
# @Програм  : Windsurf
# @Опис     : Конфигурационе поставке за апликацију Кућна Библиотека


import os
from typing import Tuple, Dict, Any

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

# File paths
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "Biblioteka.csv")
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")
LOG_PATH = os.path.join(BASE_DIR, "biblioteka.log")

# Application settings
MAX_BACKUPS = 10
DEFAULT_LANGUAGE = "sr_CYRL"
DEFAULT_THEME = "classic"
ICON_SIZE = (16, 16)

# Logging configuration
LOG_CONFIG = {
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_PATH,
            'maxBytes': 1024 * 1024,  # 1MB
            'backupCount': 5,
            'formatter': 'detailed',
            'encoding': 'utf-8'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
}

# GUI Configuration
WINDOW_MIN_SIZE: Tuple[int, int] = (1000, 700)
ICON_PATHS = {
    'app': os.path.join(BASE_DIR, 'icons', 'app_icon.png'),
    'icons_dir': os.path.join(BASE_DIR, 'icons')
}

# CSV Column Configuration
CSV_COLUMNS = [
    'Редни број', 'Наслов', 'Писац', 'Година издавања', 'Жанр',
    'Серијал', 'Колекција', 'Издавач', 'ИСБН', 'Повез', 'Напомена',
    'Позајмљена', 'Враћена', 'Ко је позајмио'
]

# Create required directories
for directory in [DATA_DIR, BACKUP_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)
