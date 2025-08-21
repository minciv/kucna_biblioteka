# -*- coding  : utf-8 -*-
# @Аутор      : minciv
# @Фајл       : models.py
# @Верзија    : 0.2.0
# @Програм    : Windsurf
# @Опис       : Модернизовани модели података за Кућну Библиотеку

# Увозимо потребне модуле
from datetime import datetime, date
from typing import Optional, List, Union
from pydantic import BaseModel, Field, validator
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
class Knjiga(BaseModel):
    """Модернизовани модел за књигу"""
    
    redni_broj: int = Field(..., description="Редни број књиге", gt=0)
    naslov: str = Field(..., description="Наслов књиге", min_length=1, max_length=500)
    pisac: str = Field(..., description="Писац/аутор књиге", min_length=1, max_length=300)
    godina_izdavanja: Optional[int] = Field(None, description="Година издавања", ge=1000, le=datetime.now().year + 1)
    zanr: Optional[str] = Field(None, description="Жанр књиге", max_length=100)
    serijal: Optional[str] = Field(None, description="Серијал коме књига припада", max_length=200)
    kolekcija: Optional[str] = Field(None, description="Колекција", max_length=200)
    izdavaci: Optional[str] = Field(None, description="Издавачи (раздвојени са ;)", max_length=300)
    isbn: Optional[str] = Field(None, description="ISBN број", max_length=20)
    povez: Optional[PovezEnum] = Field(None, description="Тип повеза")
    napomena: Optional[str] = Field(None, description="Напомена", max_length=1000)
    
    # Подаци о позајмици
    pozajmljena: bool = Field(False, description="Да ли је књига позајмљена")
    datum_pozajmice: Optional[date] = Field(None, description="Датум позајмице")
    datum_vracanja: Optional[date] = Field(None, description="Датум враћања")
    ko_je_pozajmio: Optional[str] = Field(None, description="Ко је позајмио књигу", max_length=200)
    
    # Метаподаци
    datum_dodavanja: datetime = Field(default_factory=datetime.now, description="Када је књига додата")
    poslednja_izmena: datetime = Field(default_factory=datetime.now, description="Последња измена")

    # Валидира формат писца
    @validator('pisac')
    def validiraj_pisca(cls, v):
        """Валидира формат писца"""
        if not v or not v.strip():
            raise ValueError('Писац не може бити празан')
        return v.strip()

    # Валидира ISBN
    @validator('isbn')
    def validiraj_isbn(cls, v):
        """Основна валидација ISBN-а"""
        if v:
            # Уклањамо цртице и размаке
            isbn_clean = ''.join(c for c in v if c.isdigit())
            if len(isbn_clean) not in [10, 13]:
                raise ValueError('ISBN мора имати 10 или 13 цифара')
        return v

    # Валидира датум враћања
    @validator('datum_vracanja')
    def validiraj_datum_vracanja(cls, v, values):
        """Проверава да ли је датум враћања после датума позајмице"""
        if v and 'datum_pozajmice' in values and values['datum_pozajmice']:
            if v < values['datum_pozajmice']:
                raise ValueError('Датум враћања не може бити пре датума позајмице')
        return v

    # Методи за проверу и измену статуса
    def je_pozajmljena(self) -> bool:
        """Проверава да ли је књига тренутно позајмљена"""
        return self.pozajmljena and not self.datum_vracanja

    # Позајмљује књигу
    def pozajmi_knjigu(self, ko_pozajmljuje: str, datum: Optional[date] = None) -> None:
        """Позајмљује књигу"""
        if self.je_pozajmljena():
            raise ValueError("Књига је већ позајмљена")
        
        self.pozajmljena = True
        self.ko_je_pozajmio = ko_pozajmljuje
        self.datum_pozajmice = datum or date.today()
        self.datum_vracanja = None
        self.poslednja_izmena = datetime.now()

    # Враћа књигу
    def vrati_knjigu(self, datum: Optional[date] = None) -> None:
        """Враћа књигу"""
        if not self.je_pozajmljena():
            raise ValueError("Књига није позајмљена")
        
        self.datum_vracanja = datum or date.today()
        self.pozajmljena = False
        self.poslednja_izmena = datetime.now()

    # Pydantic конфигурација
    class Config:
        """Pydantic конфигурација"""
        use_enum_values = True
        validate_assignment = True
        str_strip_whitespace = True

# Класа за писца/аутора
class Pisac(BaseModel):
    """Модел за писца/аутора"""
    
    ime: str = Field(..., description="Име писца", min_length=1, max_length=200)
    biografija: Optional[str] = Field(None, description="Кратка биографија", max_length=2000)
    godina_rodjenja: Optional[int] = Field(None, description="Година рођења", ge=1, le=datetime.now().year)
    godina_smrti: Optional[int] = Field(None, description="Година смрти", ge=1, le=datetime.now().year)
    nacionalnost: Optional[str] = Field(None, description="Националност", max_length=100)
    
    # Валидира годину смрти
    @validator('godina_smrti')
    def validiraj_godinu_smrti(cls, v, values):
        """Проверава да ли је година смрти после године рођења"""
        if v and 'godina_rodjenja' in values and values['godina_rodjenja']:
            if v < values['godina_rodjenja']:
                raise ValueError('Година смрти не може бити пре године рођења')
        return v

# Класа за издавача
class Izdavac(BaseModel):
    """Модел за издавача"""
    
    naziv: str = Field(..., description="Назив издавача", min_length=1, max_length=200)
    grad: Optional[str] = Field(None, description="Град", max_length=100)
    zemlja: Optional[str] = Field(None, description="Земља", max_length=100)
    godina_osnivanja: Optional[int] = Field(None, description="Година оснивања", ge=1400, le=datetime.now().year)
    website: Optional[str] = Field(None, description="Веб сајт", max_length=200)

# Класа за статистике библиотеке
class Statistika(BaseModel):
    """Модел за статистике библиотеке"""
    
    ukupno_knjiga: int = Field(0, description="Укупан број књига")
    pozajmljene_knjige: int = Field(0, description="Број позајмљених књига")
    dostupne_knjige: int = Field(0, description="Број доступних књига")
    broj_pisaca: int = Field(0, description="Број различитих писаца")
    broj_zanrova: int = Field(0, description="Број различитих жанрова")
    broj_izdavaca: int = Field(0, description="Број различитих издавача")
    poslednja_pozajmica: Optional[date] = Field(None, description="Датум последње позајмице")
    
    # Метаподаци
    @property
    def procenat_pozajmljenih(self) -> float:
        """Рачуна проценат позајмљених књига"""
        if self.ukupno_knjiga == 0:
            return 0.0
        return (self.pozajmljene_knjige / self.ukupno_knjiga) * 100

# Класа за конфигурацију апликације
class KonfiguracijaAplikacije(BaseModel):
    """Модел за конфигурацију апликације"""
    
    tema: str = Field("clam", description="Тема интерфејса")
    jezik: str = Field("sr_CYRL", description="Језик интерфејса")
    prikazuj_ikone: bool = Field(True, description="Приказуј иконе")
    koristi_png_ikone: bool = Field(True, description="Користи PNG иконе")
    automatski_backup: bool = Field(True, description="Аутоматски backup")
    max_backup_fajlova: int = Field(10, description="Максимални број backup фајлова", ge=1, le=100)
    log_nivo: str = Field("INFO", description="Ниво логовања")

    # Pydantic конфигурација    
    class Config:
        """Pydantic конфигурација"""
        validate_assignment = True
