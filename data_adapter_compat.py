# -*- coding: utf-8 -*-
# @Аутор   : minciv
# @Фајл     : data_adapter_compat.py
# @Верзија  : 0.2.0
# @Програм  : Windsurf
# @Опис     : Компатибилни адаптер за рад са подацима (без Pydantic зависности)

import csv
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime, date

from models_compat import Knjiga, Statistika
from config import CSV_COLUMNS, DEFAULT_DB_PATH

# Једноставно логовање без Rich зависности
def log_info(message: str):
    print(f"ℹ️  {message}")

def log_success(message: str):
    print(f"✅ {message}")

def log_error(message: str):
    print(f"❌ {message}")

def log_warning(message: str):
    print(f"⚠️  {message}")


class DataAdapterCompat(ABC):
    """Компатибилни апстрактни базни класа за адаптере података"""
    
    @abstractmethod
    def load_books(self) -> List[Knjiga]:
        """Учитава књиге из извора података"""
        pass
    
    @abstractmethod
    def save_books(self, books: List[Knjiga]) -> bool:
        """Чува књиге у извор података"""
        pass
    
    @abstractmethod
    def backup_data(self) -> bool:
        """Прави резервну копију података"""
        pass


class CSVDataAdapterCompat(DataAdapterCompat):
    """Компатибилни CSV адаптер са dataclass моделима"""
    
    def __init__(self, file_path: str = DEFAULT_DB_PATH):
        self.file_path = Path(file_path)
        self.backup_dir = self.file_path.parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def load_books(self) -> List[Knjiga]:
        """Учитава књиге из CSV фајла"""
        books = []
        
        if not self.file_path.exists():
            log_warning(f"CSV фајл не постоји: {self.file_path}")
            return books
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        book_data = self._map_csv_to_model(row)
                        book = Knjiga(**book_data)
                        books.append(book)
                    except Exception as e:
                        log_error(f"Грешка у реду {row_num}: {e}")
                        continue
            
            log_success(f"Учитано {len(books)} књига из {self.file_path}")
            
        except Exception as e:
            log_error(f"Грешка при учитавању CSV фајла: {e}")
        
        return books
    
    def save_books(self, books: List[Knjiga]) -> bool:
        """Чува књиге у CSV фајл"""
        try:
            # Прави backup пре чувања
            if self.file_path.exists():
                self.backup_data()
            
            with open(self.file_path, 'w', encoding='utf-8', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
                writer.writeheader()
                
                for book in books:
                    row = self._map_model_to_csv(book)
                    writer.writerow(row)
            
            log_success(f"Сачувано {len(books)} књига у {self.file_path}")
            return True
            
        except Exception as e:
            log_error(f"Грешка при чувању CSV фајла: {e}")
            return False
    
    def backup_data(self) -> bool:
        """Прави резервну копију CSV фајла"""
        if not self.file_path.exists():
            return True
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{self.file_path.stem}_backup_{timestamp}.csv"
            backup_path = self.backup_dir / backup_name
            
            import shutil
            shutil.copy2(self.file_path, backup_path)
            
            # Обриши старе backup-ове (задржи само 10 најновијих)
            self._cleanup_old_backups()
            
            log_success(f"Направљен backup: {backup_path}")
            return True
            
        except Exception as e:
            log_error(f"Грешка при прављењу backup-а: {e}")
            return False
    
    def _map_csv_to_model(self, row: Dict[str, str]) -> Dict:
        """Мапира CSV ред на dataclass модел"""
        # Парсирај датуме ако постоје
        datum_pozajmice = None
        datum_vracanja = None
        
        if row.get('Позајмљена') and row.get('Позајмљена').strip():
            try:
                # Покушај да парсираш датум позајмице из различитих формата
                datum_str = row.get('Позајмљена', '').strip()
                if datum_str and datum_str.lower() not in ['да', 'не', 'yes', 'no']:
                    datum_pozajmice = self._parse_date(datum_str)
            except:
                pass
        
        if row.get('Враћена') and row.get('Враћена').strip():
            try:
                datum_str = row.get('Враћена', '').strip()
                if datum_str and datum_str.lower() not in ['да', 'не', 'yes', 'no']:
                    datum_vracanja = self._parse_date(datum_str)
            except:
                pass
        
        return {
            'redni_broj': int(row.get('Редни број', 0)) or 1,
            'naslov': row.get('Наслов', '').strip(),
            'pisac': row.get('Писац', '').strip(),
            'godina_izdavanja': int(row.get('Година издавања', 0)) if row.get('Година издавања', '').strip() else None,
            'zanr': row.get('Жанр', '').strip() or None,
            'serijal': row.get('Серијал', '').strip() or None,
            'kolekcija': row.get('Колекција', '').strip() or None,
            'izdavaci': row.get('Издавачи', '').strip() or None,
            'isbn': row.get('ИСБН', '').strip() or None,
            'povez': row.get('Повез', '').strip() or None,
            'napomena': row.get('Напомена', '').strip() or None,
            'pozajmljena': row.get('Позајмљена', '').lower() in ['да', 'yes', 'true', '1'],
            'datum_pozajmice': datum_pozajmice,
            'datum_vracanja': datum_vracanja,
            'ko_je_pozajmio': row.get('Ко је позајмио', '').strip() or None,
        }
    
    def _map_model_to_csv(self, book: Knjiga) -> Dict[str, str]:
        """Мапира dataclass модел на CSV ред"""
        return {
            'Редни број': str(book.redni_broj),
            'Наслов': book.naslov,
            'Писац': book.pisac,
            'Година издавања': str(book.godina_izdavanja) if book.godina_izdavanja else '',
            'Жанр': book.zanr or '',
            'Серијал': book.serijal or '',
            'Колекција': book.kolekcija or '',
            'Издавачи': book.izdavaci or '',
            'ИСБН': book.isbn or '',
            'Повез': book.povez or '',
            'Напомена': book.napomena or '',
            'Позајмљена': 'Да' if book.pozajmljena else 'Не',
            'Враћена': str(book.datum_vracanja) if book.datum_vracanja else '',
            'Ко је позајмио': book.ko_je_pozajmio or '',
        }
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """Парсира датум из различитих формата"""
        if not date_str:
            return None
        
        formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        return None
    
    def _cleanup_old_backups(self, max_backups: int = 10):
        """Брише старе backup фајлове"""
        backup_files = list(self.backup_dir.glob(f"{self.file_path.stem}_backup_*.csv"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for old_backup in backup_files[max_backups:]:
            try:
                old_backup.unlink()
                log_info(f"Обрисан стари backup: {old_backup}")
            except Exception as e:
                log_warning(f"Не могу да обришем стари backup {old_backup}: {e}")


def calculate_statistics_compat(books: List[Knjiga]) -> Statistika:
    """Рачуна статистике за листу књига"""
    if not books:
        return Statistika()
    
    pozajmljene = [b for b in books if b.je_pozajmljena()]
    pisci = set(b.pisac for b in books)
    zanrovi = set(b.zanr for b in books if b.zanr)
    izdavaci = set()
    
    for book in books:
        if book.izdavaci:
            izdavaci.update(i.strip() for i in book.izdavaci.split(';'))
    
    poslednja_pozajmica = None
    if pozajmljene:
        datumi = [b.datum_pozajmice for b in pozajmljene if b.datum_pozajmice]
        if datumi:
            poslednja_pozajmica = max(datumi)
    
    return Statistika(
        ukupno_knjiga=len(books),
        pozajmljene_knjige=len(pozajmljene),
        dostupne_knjige=len(books) - len(pozajmljene),
        broj_pisaca=len(pisci),
        broj_zanrova=len(zanrovi),
        broj_izdavaca=len(izdavaci),
        poslednja_pozajmica=poslednja_pozajmica
    )
