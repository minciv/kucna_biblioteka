# -*- coding: utf-8 -*-
# @Author  : minciv
# @File    : statistika.py
# @Description: Помоћне функције за израчунавање статистике у Кућној библиотеци

"""
Све функције враћају податке као речнике или бројеве, погодне за директан приказ у GUI.
Сви коментари су на српском, ћирилицом.
"""

def ukupno_knjiga(data):
    """Враћа укупан број књига."""
    return len(data)

def ukupno_auta(data, podeli_pisce):
    """Враћа укупан број јединствених аутора."""
    autори = set()
    for row in data:
        for autor in podeli_pisce(row.get("Писац", "")):
            autори.add(autor)
    return len(autори)

def broj_zanrova(data):
    """Враћа број јединствених жанрова."""
    return len({row.get("Жанр", "").strip() for row in data if row.get("Жанр", "").strip()})

def broj_serijala(data):
    """Враћа број јединствених серијала."""
    return len({row.get("Серијал", "").strip() for row in data if row.get("Серијал", "").strip()})

def broj_pozajmica(data):
    """Враћа број тренутно позајмљених књига (нису враћене)."""
    return sum(1 for row in data if row.get("Позајмљена", "").strip() and not row.get("Враћена", "").strip())

def knjige_po_zanru(data):
    """Враћа речник: жанр -> број књига."""
    rez = {}
    for row in data:
        zanr = row.get("Жанр", "").strip()
        if zanr:
            rez[zanr] = rez.get(zanr, 0) + 1
    return rez

def knjige_po_izdavacu(data):
    """Враћа речник: издавач -> број књига."""
    rez = {}
    for row in data:
        izdavac = row.get("Издавач", "").strip()
        if izdavac:
            rez[izdavac] = rez.get(izdavac, 0) + 1
    return rez

def top_autori(data, podeli_pisce, top_n=5):
    """Враћа листу топ N аутора као (име, број књига)."""
    autori_broj = {}
    for row in data:
        for autor in podeli_pisce(row.get("Писац", "")):
            autori_broj[autor] = autori_broj.get(autor, 0) + 1
    return sorted(autori_broj.items(), key=lambda x: x[1], reverse=True)[:top_n]
