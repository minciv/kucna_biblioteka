# -*- coding: utf-8 -*-
# @Аутор   : minciv
# @Фајл     : book_service.py
# @Верзија  : 0.2.0
# @Програм  : Windsurf
# @Опис     : Модернизовани сервис за управљање књигама

from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime
import re

from models import Knjiga, Pisac, Izdavac, Statistika
from data_adapter import DataAdapter, CSVDataAdapter, calculate_statistics
from logger import get_logger, log_success, log_error, log_warning

logger = get_logger(__name__)


class BookService:
    """Модернизовани сервис за управљање књигама"""
    
    def __init__(self, data_adapter: Optional[DataAdapter] = None):
        self.data_adapter = data_adapter or CSVDataAdapter()
        self._books: List[Knjiga] = []
        self._loaded = False
    
    def load_books(self) -> bool:
        """Учитава књиге из извора података"""
        try:
            self._books = self.data_adapter.load_books()
            self._loaded = True
            log_success(f"Учитано {len(self._books)} књига")
            return True
        except Exception as e:
            log_error(f"Грешка при учитавању књига: {e}")
            return False
    
    def save_books(self) -> bool:
        """Чува књиге у извор података"""
        try:
            success = self.data_adapter.save_books(self._books)
            if success:
                log_success(f"Сачувано {len(self._books)} књига")
            return success
        except Exception as e:
            log_error(f"Грешка при чувању књига: {e}")
            return False
    
    def get_all_books(self) -> List[Knjiga]:
        """Враћа све књиге"""
        if not self._loaded:
            self.load_books()
        return self._books.copy()
    
    def get_book_by_id(self, redni_broj: int) -> Optional[Knjiga]:
        """Враћа књигу по редном броју"""
        for book in self._books:
            if book.redni_broj == redni_broj:
                return book
        return None
    
    def add_book(self, book: Knjiga) -> bool:
        """Додаје нову књигу"""
        try:
            # Провери да ли већ постоји књига са истим редним бројем
            if self.get_book_by_id(book.redni_broj):
                log_error(f"Књига са редним бројем {book.redni_broj} већ постоји")
                return False
            
            self._books.append(book)
            log_success(f"Додата књига: {book.naslov}")
            return True
        except Exception as e:
            log_error(f"Грешка при додавању књиге: {e}")
            return False
    
    def update_book(self, redni_broj: int, updated_book: Knjiga) -> bool:
        """Ажурира постојећу књигу"""
        try:
            for i, book in enumerate(self._books):
                if book.redni_broj == redni_broj:
                    updated_book.poslednja_izmena = datetime.now()
                    self._books[i] = updated_book
                    log_success(f"Ажурирана књига: {updated_book.naslov}")
                    return True
            
            log_error(f"Књига са редним бројем {redni_broj} није пронађена")
            return False
        except Exception as e:
            log_error(f"Грешка при ажурирању књиге: {e}")
            return False
    
    def delete_book(self, redni_broj: int) -> bool:
        """Брише књигу"""
        try:
            for i, book in enumerate(self._books):
                if book.redni_broj == redni_broj:
                    deleted_book = self._books.pop(i)
                    log_success(f"Обрисана књига: {deleted_book.naslov}")
                    return True
            
            log_error(f"Књига са редним бројем {redni_broj} није пронађена")
            return False
        except Exception as e:
            log_error(f"Грешка при брисању књиге: {e}")
            return False
    
    def search_books(self, query: str, field: Optional[str] = None) -> List[Knjiga]:
        """Претражује књиге по различитим критеријумима"""
        if not query.strip():
            return self._books.copy()
        
        query_lower = query.lower().strip()
        results = []
        
        for book in self._books:
            match = False
            
            if field is None:
                # Претрага по свим пољима
                searchable_fields = [
                    book.naslov, book.pisac, book.zanr or '', 
                    book.serijal or '', book.izdavaci or '', 
                    book.napomena or ''
                ]
                match = any(query_lower in field.lower() for field in searchable_fields)
            else:
                # Претрага по конкретном пољу
                field_value = getattr(book, field, '')
                if field_value:
                    match = query_lower in str(field_value).lower()
            
            if match:
                results.append(book)
        
        log_success(f"Пронађено {len(results)} књига за претрагу: '{query}'")
        return results
    
    def get_available_books(self) -> List[Knjiga]:
        """Враћа доступне (непозајмљене) књиге"""
        return [book for book in self._books if not book.je_pozajmljena()]
    
    def get_loaned_books(self) -> List[Knjiga]:
        """Враћа позајмљене књиге"""
        return [book for book in self._books if book.je_pozajmljena()]
    
    def loan_book(self, redni_broj: int, borrower: str, loan_date: Optional[date] = None) -> bool:
        """Позајмљује књигу"""
        try:
            book = self.get_book_by_id(redni_broj)
            if not book:
                log_error(f"Књига са редним бројем {redni_broj} није пронађена")
                return False
            
            if book.je_pozajmljena():
                log_error(f"Књига '{book.naslov}' је већ позајмљена")
                return False
            
            book.pozajmi_knjigu(borrower, loan_date)
            log_success(f"Књига '{book.naslov}' позајмљена кориснику {borrower}")
            return True
        except Exception as e:
            log_error(f"Грешка при позајмљивању књиге: {e}")
            return False
    
    def return_book(self, redni_broj: int, return_date: Optional[date] = None) -> bool:
        """Враћа позајмљену књигу"""
        try:
            book = self.get_book_by_id(redni_broj)
            if not book:
                log_error(f"Књига са редним бројем {redni_broj} није пронађена")
                return False
            
            if not book.je_pozajmljena():
                log_error(f"Књига '{book.naslov}' није позајмљена")
                return False
            
            borrower = book.ko_je_pozajmio
            book.vrati_knjigu(return_date)
            log_success(f"Књига '{book.naslov}' враћена од корисника {borrower}")
            return True
        except Exception as e:
            log_error(f"Грешка при враћању књиге: {e}")
            return False
    
    def get_statistics(self) -> Statistika:
        """Рачуна и враћа статистике библиотеке"""
        return calculate_statistics(self._books)
    
    def get_unique_values(self, field: str) -> List[str]:
        """Враћа јединствене вредности за дато поље"""
        values = set()
        
        for book in self._books:
            field_value = getattr(book, field, None)
            if field_value:
                if field == 'izdavaci' and ';' in field_value:
                    # За издаваче који могу бити раздвојени са ;
                    values.update(v.strip() for v in field_value.split(';'))
                else:
                    values.add(str(field_value).strip())
        
        return sorted(list(values))
    
    def get_authors(self) -> List[str]:
        """Враћа листу свих аутора"""
        return self.get_unique_values('pisac')
    
    def get_genres(self) -> List[str]:
        """Враћа листу свих жанрова"""
        return self.get_unique_values('zanr')
    
    def get_publishers(self) -> List[str]:
        """Враћа листу свих издавача"""
        return self.get_unique_values('izdavaci')
    
    def get_series(self) -> List[str]:
        """Враћа листу свих серијала"""
        return self.get_unique_values('serijal')
    
    def validate_isbn(self, isbn: str) -> bool:
        """Валидира ISBN број"""
        if not isbn:
            return True  # Празан ISBN је дозвољен
        
        # Уклони све што није цифра
        digits_only = re.sub(r'[^0-9]', '', isbn)
        
        # Провери дужину
        if len(digits_only) not in [10, 13]:
            return False
        
        # За сада само основна провера дужине
        # Можда додати checksum валидацију касније
        return True
    
    def get_next_available_id(self) -> int:
        """Враћа следећи доступни редни број"""
        if not self._books:
            return 1
        
        existing_ids = {book.redni_broj for book in self._books}
        next_id = 1
        
        while next_id in existing_ids:
            next_id += 1
        
        return next_id
    
    def export_to_dict(self) -> List[Dict[str, Any]]:
        """Извози књиге у речник формат за JSON/Excel"""
        return [book.dict() for book in self._books]
    
    def import_from_dict(self, books_data: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Увози књиге из речник формата"""
        imported = 0
        errors = 0
        
        for book_data in books_data:
            try:
                book = Knjiga(**book_data)
                if self.add_book(book):
                    imported += 1
                else:
                    errors += 1
            except Exception as e:
                log_error(f"Грешка при увозу књиге: {e}")
                errors += 1
        
        log_success(f"Увезено {imported} књига, {errors} грешака")
        return imported, errors
    
    def backup_data(self) -> bool:
        """Прави резервну копију података"""
        try:
            return self.data_adapter.backup_data()
        except Exception as e:
            log_error(f"Грешка при прављењу резервне копије: {e}")
            return False
