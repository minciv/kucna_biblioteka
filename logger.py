# -*- coding: utf-8 -*-
# @Аутор    : minciv
# @Фајл     : logger.py
# @Верзија  : 0.2.0
# @Програм  : Windsurf
# @Опис     : Модернизована конфигурација логовања за апликацију Библиотека

import logging
import logging.config
from typing import Optional
from config import LOG_CONFIG, LOG_PATH

# Покушај да увезеш Rich, ако није доступан користи стандардно логовање
try:
    from rich.logging import RichHandler
    from rich.console import Console
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RichHandler = None
    console = None
    RICH_AVAILABLE = False

def setup_logging(use_rich: bool = True, log_level: str = "INFO"):
    """
    Подешава модернизовану конфигурацију логовања
    
    Args:
        use_rich: Користи Rich за боље форматирање излаза
        log_level: Ниво логовања (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    if use_rich and RICH_AVAILABLE:
        # Модернизована конфигурација са Rich
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format="%(message)s",
            datefmt="[%X]",
            handlers=[
                RichHandler(
                    console=console,
                    show_time=True,
                    show_level=True,
                    show_path=True,
                    markup=True,
                    rich_tracebacks=True
                ),
                logging.FileHandler(
                    LOG_PATH, 
                    encoding='utf-8',
                    mode='a'
                )
            ]
        )
    else:
        # Стандардна конфигурација за компатибилност
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(
                    LOG_PATH, 
                    encoding='utf-8',
                    mode='a'
                )
            ]
        )

def get_logger(name: str) -> logging.Logger:
    """Враћа инстанцу логера са датим именом"""
    return logging.getLogger(name)

def log_app_info(message: str):
    """Логује информације о апликацији са лепим форматирањем"""
    if RICH_AVAILABLE and console:
        console.print(f"[bold blue]📚 Кућна Библиотека:[/bold blue] {message}")
    else:
        print(f"📚 Кућна Библиотека: {message}")

def log_success(message: str):
    """Логује успешне операције"""
    if RICH_AVAILABLE and console:
        console.print(f"[bold green]✅ Успех:[/bold green] {message}")
    else:
        print(f"✅ Успех: {message}")

def log_warning(message: str):
    """Логује упозорења"""
    if RICH_AVAILABLE and console:
        console.print(f"[bold yellow]⚠️  Упозорење:[/bold yellow] {message}")
    else:
        print(f"⚠️  Упозорење: {message}")

def log_error(message: str):
    """Логује грешке"""
    if RICH_AVAILABLE and console:
        console.print(f"[bold red]❌ Грешка:[/bold red] {message}")
    else:
        print(f"❌ Грешка: {message}")
