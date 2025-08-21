# -*- coding: utf-8 -*-
# @Аутор    : minciv
# @Фајл     : models_compat.py
# @Верзија  : 0.2.0
# @Програм  : Windsurf
# @Опис     : Компатибилни модели података без Pydantic зависности

# Увозимо потребне модуле
from datetime import datetime, date
from typing import Optional, List, Union, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

# Енумерација за типове повеза
class PovezEnum(str, Enum):
    """Енумерација за типове повеза"""
    TVRDI = "Тврди повез"
    MEKI = "Меки повез"
    SPIRALNI = "Спирални повез"
    OSTALO = "Остало"

# Енумерација за статус позајмице
class StatusPozajmiceEnum(str, Enum):
    """Енумерација за статус позајмице"""
    DOSTUPNA = "Доступна"
    POZAJMLJENA = "Позајмљена"
    VRACENA = "Враћена"

# Класа за књигу
@dataclass
class Knjiga:
    """Компатибилни модел за књигу користећи dataclass"""
    
    redni_broj: int
    naslov: str
    pisac: str
    godina_izdavanja: Optional[int] = None
    zanr: Optional[str] = None
    serijal: Optional[str] = None
    kolekcija: Optional[str] = None
    izdavaci: Optional[str] = None
    isbn: Optional[str] = None
    povez: Optional[str] = None
    napomena: Optional[str] = None
    
    # Подаци о позајмици
    pozajmljena: bool = False
    datum_pozajmice: Optional[date] = None
    datum_vracanja: Optional[date] = None
    ko_je_pozajmio: Optional[str] = None
    
    # Метаподаци
    datum_dodavanja: datetime = field(default_factory=datetime.now)
    poslednja_izmena: datetime = field(default_factory=datetime.now)

    # Метод за валидацију
    def __post_init__(self):
        """Валидација након иницијализације"""
        if self.redni_broj <= 0:
            raise ValueError('Редни број мора бити већи од 0')
        
        if not self.naslov or not self.naslov.strip():
            raise ValueError('Наслов не може бити празан')
        
        if not self.pisac or not self.pisac.strip():
            raise ValueError('Писац не може бити празан')
        
        # Очисти белине
        self.naslov = self.naslov.strip()
        self.pisac = self.pisac.strip()
        
        if self.zanr:
            self.zanr = self.zanr.strip()
        if self.serijal:
            self.serijal = self.serijal.strip()
        if self.kolekcija:
            self.kolekcija = self.kolekcija.strip()
        if self.izdavaci:
            self.izdavaci = self.izdavaci.strip()
        if self.isbn:
            self.isbn = self.isbn.strip()
        if self.napomena:
            self.napomena = self.napomena.strip()
        if self.ko_je_pozajmio:
            self.ko_je_pozajmio = self.ko_je_pozajmio.strip()

    # Метод за проверу да ли је књига позајмљена
    def je_pozajmljena(self) -> bool:
        """Проверава да ли је књига тренутно позајмљена"""
        return self.pozajmljena and not self.datum_vracanja

    # Метод за позајмљуње књиге
    def pozajmi_knjigu(self, ko_pozajmljuje: str, datum: Optional[date] = None) -> None:
        """Позајмљује књигу"""
        if self.je_pozajmljena():
            raise ValueError("Књига је већ позајмљена")
        
        self.pozajmljena = True
        self.ko_je_pozajmio = ko_pozajmljuje.strip()
        self.datum_pozajmice = datum or date.today()
        self.datum_vracanja = None
        self.poslednja_izmena = datetime.now()

    # Метод за враћање књиге
    def vrati_knjigu(self, datum: Optional[date] = None) -> None:
        """Враћа књигу"""
        if not self.je_pozajmljena():
            raise ValueError("Књига није позајмљена")
        
        self.datum_vracanja = datum or date.today()
        self.pozajmljena = False
        self.poslednja_izmena = datetime.now()

    # Метод за конвертирање у речник
    def to_dict(self) -> Dict[str, Any]:
        """Конвертује у речник"""
        return {
            'redni_broj': self.redni_broj,
            'naslov': self.naslov,
            'pisac': self.pisac,
            'godina_izdavanja': self.godina_izdavanja,
            'zanr': self.zanr,
            'serijal': self.serijal,
            'kolekcija': self.kolekcija,
            'izdavaci': self.izdavaci,
            'isbn': self.isbn,
            'povez': self.povez,
            'napomena': self.napomena,
            'pozajmljena': self.pozajmljena,
            'datum_pozajmice': self.datum_pozajmice.isoformat() if self.datum_pozajmice else None,
            'datum_vracanja': self.datum_vracanja.isoformat() if self.datum_vracanja else None,
            'ko_je_pozajmio': self.ko_je_pozajmio,
            'datum_dodavanja': self.datum_dodavanja.isoformat(),
            'poslednja_izmena': self.poslednja_izmena.isoformat()
        }

    # Статичка функција за креирање инстанце из речника
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Knjiga':
        """Креира инстанцу из речника"""
        # Конвертуј датуме из string формата
        if data.get('datum_pozajmice'):
            data['datum_pozajmice'] = date.fromisoformat(data['datum_pozajmice'])
        if data.get('datum_vracanja'):
            data['datum_vracanja'] = date.fromisoformat(data['datum_vracanja'])
        if data.get('datum_dodavanja'):
            data['datum_dodavanja'] = datetime.fromisoformat(data['datum_dodavanja'])
        if data.get('poslednja_izmena'):
            data['poslednja_izmena'] = datetime.fromisoformat(data['poslednja_izmena'])
        
        return cls(**data)


# Класа за писца
@dataclass
class Pisac:
    """Компатибилни модел за писца"""
    
    ime: str
    biografija: Optional[str] = None
    godina_rodjenja: Optional[int] = None
    godina_smrti: Optional[int] = None
    nacionalnost: Optional[str] = None

    # Метод за валидацију
    def __post_init__(self):
        if not self.ime or not self.ime.strip():
            raise ValueError('Име писца не може бити празно')
        
        self.ime = self.ime.strip()
        
        if self.biografija:
            self.biografija = self.biografija.strip()
        if self.nacionalnost:
            self.nacionalnost = self.nacionalnost.strip()
        
        # Валидација година
        if (self.godina_smrti and self.godina_rodjenja and 
            self.godina_smrti < self.godina_rodjenja):
            raise ValueError('Година смрти не може бити пре године рођења')

# Класа за издавача
@dataclass
class Izdavac:
    """Компатибилни модел за издавача"""
    
    naziv: str
    grad: Optional[str] = None
    zemlja: Optional[str] = None
    godina_osnivanja: Optional[int] = None
    website: Optional[str] = None

    # Метод за валидацију
    def __post_init__(self):
        if not self.naziv or not self.naziv.strip():
            raise ValueError('Назив издавача не може бити празан')
        
        self.naziv = self.naziv.strip()
        
        if self.grad:
            self.grad = self.grad.strip()
        if self.zemlja:
            self.zemlja = self.zemlja.strip()
        if self.website:
            self.website = self.website.strip()

# Класа за статистике библиотеке
@dataclass
class Statistika:
    """Компатибилни модел за статистике библиотеке"""
    
    ukupno_knjiga: int = 0
    pozajmljene_knjige: int = 0
    dostupne_knjige: int = 0
    broj_pisaca: int = 0
    broj_zanrova: int = 0
    broj_izdavaca: int = 0
    poslednja_pozajmica: Optional[date] = None

    # Статусни методи
    @property
    def procenat_pozajmljenih(self) -> float:
        """Рачуна проценат позајмљених књига"""
        if self.ukupno_knjiga == 0:
            return 0.0
        return (self.pozajmljene_knjige / self.ukupno_knjiga) * 100

# Класа за конфигурацију апликације
@dataclass
class KonfiguracijaAplikacije:
    """Компатибилни модел за конфигурацију апликације"""
    
    tema: str = "clam"
    jezik: str = "sr_CYRL"
    prikazuj_ikone: bool = True
    koristi_png_ikone: bool = True
    automatski_backup: bool = True
    max_backup_fajlova: int = 10
    log_nivo: str = "INFO"

    # Метод за валидацију
    def __post_init__(self):
        if self.max_backup_fajlova < 1 or self.max_backup_fajlova > 100:
            raise ValueError('Број backup фајлова мора бити између 1 и 100')


# Помоћне функције за валидацију
def validate_isbn(isbn: str) -> bool:
    """Валидира ISBN број"""
    if not isbn:
        return True
    
    import re
    digits_only = re.sub(r'[^0-9]', '', isbn)
    return len(digits_only) in [10, 13]

# Функција за валидацију године
def validate_year(year: Optional[int]) -> bool:
    """Валидира годину"""
    if year is None:
        return True
    
    current_year = datetime.now().year
    return 1000 <= year <= current_year + 1