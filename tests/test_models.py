# -*- coding: utf-8 -*-
# @Аутор   : minciv
# @Фајл     : tests/test_models.py
# @Верзија  : 0.2.0
# @Програм  : Windsurf
# @Опис     : Тестови за модернизоване моделе података

import pytest
from datetime import date, datetime
from pydantic import ValidationError

from models import Knjiga, Pisac, Izdavac, ПовезEnum, StatusPozajmiceEnum


class TestKnjiga:
    """Тестови за модел Knjiga"""
    
    def test_kreiranje_osnovne_knjige(self):
        """Тест креирања основне књиге"""
        knjiga = Knjiga(
            redni_broj=1,
            naslov="Тест књига",
            pisac="Тест аутор"
        )
        
        assert knjiga.redni_broj == 1
        assert knjiga.naslov == "Тест књига"
        assert knjiga.pisac == "Тест аутор"
        assert not knjiga.pozajmljena
        assert knjiga.datum_dodavanja is not None

    def test_kreiranje_kompletne_knjige(self):
        """Тест креирања књиге са свим пољима"""
        knjiga = Knjiga(
            redni_broj=1,
            naslov="Тест књига",
            pisac="Тест аутор",
            godina_izdavanja=2023,
            zanr="Фантастика",
            serijal="Тест серијал",
            kolekcija="Тест колекција",
            izdavaci="Тест издавач",
            isbn="978-86-123-4567-8",
            povez=ПовезEnum.TVRDI,
            napomena="Тест напомена"
        )
        
        assert knjiga.godina_izdavanja == 2023
        assert knjiga.zanr == "Фантастика"
        assert knjiga.povez == ПовезEnum.TVRDI

    def test_validacija_rednog_broja(self):
        """Тест валидације редног броја"""
        with pytest.raises(ValidationError):
            Knjiga(
                redni_broj=0,  # Неважећи редни број
                naslov="Тест",
                pisac="Тест"
            )

    def test_validacija_isbn(self):
        """Тест валидације ISBN-а"""
        # Важећи ISBN-10
        knjiga1 = Knjiga(
            redni_broj=1,
            naslov="Тест",
            pisac="Тест",
            isbn="86-123-4567-8"
        )
        assert knjiga1.isbn == "86-123-4567-8"
        
        # Важећи ISBN-13
        knjiga2 = Knjiga(
            redni_broj=2,
            naslov="Тест",
            pisac="Тест",
            isbn="978-86-123-4567-8"
        )
        assert knjiga2.isbn == "978-86-123-4567-8"
        
        # Неважећи ISBN
        with pytest.raises(ValidationError):
            Knjiga(
                redni_broj=3,
                naslov="Тест",
                pisac="Тест",
                isbn="123"  # Превише кратак
            )

    def test_pozajmljivanje_knjige(self):
        """Тест позајмљивања књиге"""
        knjiga = Knjiga(
            redni_broj=1,
            naslov="Тест",
            pisac="Тест"
        )
        
        # Позајми књигу
        knjiga.pozajmi_knjigu("Марко Петровић")
        
        assert knjiga.je_pozajmljena()
        assert knjiga.ko_je_pozajmio == "Марко Петровић"
        assert knjiga.datum_pozajmice == date.today()
        assert knjiga.datum_vracanja is None

    def test_vracanje_knjige(self):
        """Тест враћања књиге"""
        knjiga = Knjiga(
            redni_broj=1,
            naslov="Тест",
            pisac="Тест"
        )
        
        # Позајми па врати
        knjiga.pozajmi_knjigu("Марко Петровић")
        knjiga.vrati_knjigu()
        
        assert not knjiga.je_pozajmljena()
        assert knjiga.datum_vracanja == date.today()

    def test_duplo_pozajmljivanje(self):
        """Тест да се не може дупло позајмити"""
        knjiga = Knjiga(
            redni_broj=1,
            naslov="Тест",
            pisac="Тест"
        )
        
        knjiga.pozajmi_knjigu("Марко Петровић")
        
        with pytest.raises(ValueError, match="Књига је већ позајмљена"):
            knjiga.pozajmi_knjigu("Ана Јовановић")


class TestPisac:
    """Тестови за модел Pisac"""
    
    def test_kreiranje_pisca(self):
        """Тест креирања писца"""
        pisac = Pisac(
            ime="Иво Андрић",
            biografija="Српски писац, нобеловац",
            godina_rodjenja=1892,
            godina_smrti=1975,
            nacionalnost="Српска"
        )
        
        assert pisac.ime == "Иво Андрић"
        assert pisac.godina_rodjenja == 1892
        assert pisac.godina_smrti == 1975

    def test_validacija_godina(self):
        """Тест валидације година"""
        with pytest.raises(ValidationError):
            Pisac(
                ime="Тест",
                godina_rodjenja=1950,
                godina_smrti=1940  # Смрт пре рођења
            )


class TestIzdavac:
    """Тестови за модел Izdavac"""
    
    def test_kreiranje_izdavaca(self):
        """Тест креирања издавача"""
        izdavac = Izdavac(
            naziv="Лагуна",
            grad="Београд",
            zemlja="Србија",
            godina_osnivanja=1995
        )
        
        assert izdavac.naziv == "Лагуна"
        assert izdavac.grad == "Београд"
        assert izdavac.zemlja == "Србија"


if __name__ == "__main__":
    pytest.main([__file__])
