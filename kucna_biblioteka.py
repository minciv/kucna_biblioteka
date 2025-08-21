# -*- coding: utf-8 -*-
# @Аутор    : minciv
# @Фајл     : kucna_biblioteka.py
# @Верзија  : 0.2.0
# @Програм  : Windsurf
# @Опис     : Модернизована главна датотека за покретање програма Кућна Библиотека

# Увозимо потребне модуле
import sys
import os
from typing import Optional
from pathlib import Path

from logger import setup_logging, get_logger, log_app_info, log_error, log_warning
from config import DEFAULT_DB_PATH, BASE_DIR
from biblioteka_gui import main

logger = get_logger(__name__)

# Функција за проверу зависности
def check_dependencies() -> bool:
    """Проверава да ли су све потребне зависности инсталиране"""
    # Основни модули који су обавезни
    required_modules = ['tkinter']
    # Опциони модули који побољшавају функционалност
    optional_modules = ['pandas', 'matplotlib', 'PIL', 'pydantic', 'rich']
    
    missing_required = []
    missing_optional = []
    
    # Проверавање обавезних модула
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_required.append(module)
    
    # Проверавање опционалних модула
    for module in optional_modules:
        try:
            __import__(module)
        except ImportError:
            missing_optional.append(module)
    
    # Проверавање обавезних модула
    if missing_required:
        log_error(f"Недостају обавезни модули: {', '.join(missing_required)}")
        log_error("Инсталирајте их помоћу: pip install -r requirements.txt")
        return False
    
    # Проверавање опционалних модула
    if missing_optional:
        log_warning(f"Недостају опциони модули: {', '.join(missing_optional)}")
        log_warning("За пуну функционалност инсталирајте: pip install -r requirements.txt")
        log_app_info("Апликација ће радити са ограниченом функционалношћу")
    
    return True

# Функција за проверу фајлова
def ensure_data_files() -> bool:
    """Осигурава да постоје потребни фајлови"""
    csv_path = Path(DEFAULT_DB_PATH)
    example_path = Path(BASE_DIR) / "Biblioteka.csv.example"
    
    # Ако не постоји главни CSV фајл, покушај да копираш пример
    if not csv_path.exists() and example_path.exists():
        try:
            import shutil
            shutil.copy2(example_path, csv_path)
            log_app_info(f"Копиран пример фајл у {csv_path}")
        except Exception as e:
            log_error(f"Не могу да копирам пример фајл: {e}")
            return False
    
    return True

# Функција за иницијализацију апликације
def init_app(db_path: Optional[str] = None) -> None:
    """
    Иницијализује апликацију са модернизованим провераме
    
    Args:
        db_path: Путања до CSV фајла са подацима
    """
    # Подеси логовање
    setup_logging(use_rich=True, log_level="INFO")
    
    log_app_info("Покретање Кућне Библиотеке v0.2.0")
    
    # Провери зависности
    if not check_dependencies():
        log_error("Неуспешна провера зависности")
        sys.exit(1)
    
    # Провери и припреми фајлове
    if not ensure_data_files():
        log_error("Неуспешна припрема фајлова")
        sys.exit(1)
    
    # Користи задату путању или подразумевану
    final_db_path = db_path or DEFAULT_DB_PATH
    
    logger.info(f"Покретање апликације са базом: {final_db_path}")
    
    try:
        main(final_db_path)
        log_app_info("Апликација успешно затворена")
    except KeyboardInterrupt:
        log_app_info("Апликација прекинута од стране корисника")
        sys.exit(0)
    except Exception as e:
        logger.exception("Критична грешка при покретању апликације")
        log_error(f"Критична грешка: {e}")
        sys.exit(1)

# Главна функција за CLI покретање
def main_cli():
    """Главна функција за CLI покретање"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Кућна Библиотека - Апликација за управљање књигама",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примери коришћења:
  python kucna_biblioteka.py                    # Покрени са подразумеваним фајлом
  python kucna_biblioteka.py --db mojabaza.csv  # Покрени са другим фајлом
  python kucna_biblioteka.py --version          # Прикажи верзију
        """
    )
    
    parser.add_argument(
        '--db', '--database',
        type=str,
        help='Путања до CSV фајла са подацима'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Кућна Библиотека v0.2.0'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Покрени у debug режиму'
    )
    
    args = parser.parse_args()
    
    # Подеси ниво логовања
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging(use_rich=True, log_level=log_level)
    
    # Покрени апликацију
    init_app(args.db)

# Главна функција за CLI покретање
if __name__ == "__main__":
    main_cli()
