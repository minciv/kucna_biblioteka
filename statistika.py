# -*- coding: utf-8 -*-
# @Аутор    : minciv
# @Фајл     : statistika.py
# @Верзија  : 0.2.0
# @Програм  : Windsurf
# @Опис     : Помоћне функције за израчунавање статистике у Кућној библиотеци

"""
Све функције враћају податке као речнике или бројеве, погодне за директан приказ у GUI.
Сви коментари су на српском, ћирилицом.
"""

# Функције за статистику по броју књига
def ukupno_knjiga(data):
    """Враћа укупан број књига."""
    return len(data)

# Функције за статистику по броју аутора
def ukupno_autora(data, podeli_pisce):
    """Враћа укупан број јединствених аутора."""
    autori = set()
    for row in data:
        for autor in podeli_pisce(row.get("Писац", "")):
            autori.add(autor)
    return len(autori)

# Функције за статистику по броју жанрова
def broj_zanrova(data):
    """Враћа број јединствених жанрова."""
    return len({row.get("Жанр", "").strip() for row in data if row.get("Жанр", "").strip()})

# Функције за статистику по броју серијала
def broj_serijala(data):
    """Враћа број јединствених серијала."""
    return len({row.get("Серијал", "").strip() for row in data if row.get("Серијал", "").strip()})

# Функције за статистику по броју позајмљених књига
def broj_pozajmica(data):
    """Враћа број тренутно позајмљених књига (нису враћене)."""
    return sum(1 for row in data if row.get("Позајмљена", "").strip() and not row.get("Враћена", "").strip())

# Функције за статистику по броју књига по жанру
def knjige_po_zanru(data):
    """Враћа речник: жанр -> број књига."""
    rez = {}
    for row in data:
        zanr = row.get("Жанр", "").strip()
        if zanr:
            rez[zanr] = rez.get(zanr, 0) + 1
    return rez

# Функције за статистику по броју књига по издавачу
def knjige_po_izdavacu(data):
    """Враћа речник: издавач -> број књига."""
    rez = {}
    for row in data:
        izdavac = row.get("Издавач", "").strip()
        if izdavac:
            rez[izdavac] = rez.get(izdavac, 0) + 1
    return rez

# Функције за статистику по броју топ N аутора
def top_autori(data, podeli_pisce, top_n=5):
    """Враћа листу топ N аутора као (име, број књига)."""
    autori_broj = {}
    for row in data:
        for autor in podeli_pisce(row.get("Писац", "")):
            autori_broj[autor] = autori_broj.get(autor, 0) + 1
    return sorted(autori_broj.items(), key=lambda x: x[1], reverse=True)[:top_n]