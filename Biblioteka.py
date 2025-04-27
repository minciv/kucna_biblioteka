# -*- coding: utf-8 -*-
# @Аутор   : minciv
# @Фајл     : Biblioteka.py
# @Верзија  : 0.0.01.02.
# @Програм  : Windsurf
# @Опис     : Датотека за управљање подацима о књигама

import os
import csv

# Иницијализација глобалних променљивих
zanr = []
izdavac = []
povez = []
pisci = []

def ucitaj_podatke(putanja_do_csv):
    """Учитава податке из CSV фајла."""
    try:
        with open(putanja_do_csv, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)
            return data
    except FileNotFoundError:
        print(f"Грешка: Фајл није пронађен: {putanja_do_csv}")
        return []
    except Exception as e:
        print(f"Грешка приликом читања фајла: {e}")
        return []

def dobavi_sve_pisce(podaci):
    """Извлачи све писце из базе података и враћа их као регистар."""
    pisci_set = set()
    
    for knjiga in podaci:
        pisci_text = knjiga.get("Писац", "")
        if pisci_text:
            # Раздваја списак писаца по ';' и чисти белине
            pisci_lista = [p.strip() for p in pisci_text.split(';')]
            # Додаје писце у сет
            for pisac in pisci_lista:
                if pisac:  # Проверава да ли је празан стринг
                    pisci_set.add(pisac)
    
    # Претвара сет у сортирану листу
    return sorted(list(pisci_set))

def podeli_pisce(pisci_text):
    """Дели текст писаца раздвојен са ';' у листу писаца."""
    if not pisci_text:
        return []
    return [p.strip() for p in pisci_text.split(';') if p.strip()]

def inicijalizuj_podatke(putanja_do_csv=None):
    """Иницијализује глобалне променљиве на основу података из CSV фајла."""
    global zanr, izdavac, povez, pisci
    
    # Ако није задата путања, покушај да нађеш CSV у истом директоријуму
    if putanja_do_csv is None:
        putanja_do_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Biblioteka.csv')
    
    podaci = ucitaj_podatke(putanja_do_csv)
    
    # Извлачи јединствене вредности из колона
    zanr_set = {row.get("Жанр", "").strip() for row in podaci if row.get("Жанр", "").strip() != ""}
    zanr = sorted(list(zanr_set)) if zanr_set else []
    
    # Извлачи издаваче (слично као за писце, подржава вишеструке издаваче)
    izdavac_set = set()
    for row in podaci:
        # Прво проверавамо ново поље "Издавачи"
        if row.get("Издавачи", "").strip():
            for izdavac_item in row.get("Издавачи", "").split(";"):
                izdavac_item = izdavac_item.strip()
                if izdavac_item:
                    izdavac_set.add(izdavac_item)
        # Затим проверавамо и старо поље "Издавач"
        elif row.get("Издавач", "").strip():
            for izdavac_item in row.get("Издавач", "").split(";"):
                izdavac_item = izdavac_item.strip()
                if izdavac_item:
                    izdavac_set.add(izdavac_item)
    izdavac = sorted(list(izdavac_set)) if izdavac_set else []
    
    povez_set = {row.get("Повез", "").strip() for row in podaci if row.get("Повез", "").strip() != ""}
    povez = sorted(list(povez_set)) if povez_set else []
    
    # Креира регистар писаца
    pisci = dobavi_sve_pisce(podaci)
    
    return {
        'zanr': zanr,
        'izdavac': izdavac,
        'povez': povez,
        'pisci': pisci
    }

def sacuvaj_podatke(putanja_do_csv, podaci):
    """Сачувава податке у CSV фајл. Пре сваког чувања прави резервну копију (backup)."""
    try:
        # --- Резервна копија пре сваке измене ---
        from backup_utils import napravi_backup
        napravi_backup(putanja_do_csv)
        # --- Крај backup блока ---
        
        # Пре чувања, проверавамо податке за компатибилност
        for knjiga in podaci:
            # Ако књига садржи поље "Издавачи", копирамо га у "Издавач" и уклањамо га
            if "Издавачи" in knjiga:
                knjiga["Издавач"] = knjiga["Издавачи"]
                del knjiga["Издавачи"]
        
        with open(putanja_do_csv, 'w', newline='', encoding='utf-8') as csvfile:
            # Правимо листу поља за CSV
            fieldnames = ['Редни број']
            # Додајемо само поља која постоје у подацима
            for knjiga in podaci:
                for key in knjiga.keys():
                    if key != 'Редни број' and key not in fieldnames:
                        fieldnames.append(key)
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(podaci)
        return True
    except Exception as e:
        print(f"Грешка приликом писања у фајл: {e}")
        return False

def dodaj_knjigu(putanja_do_csv, nova_knjiga):
    """Додаје нову књигу у библиотеку."""
    podaci = ucitaj_podatke(putanja_do_csv)
    nova_knjiga["Редни број"] = str(len(podaci) + 1)
    podaci.append(nova_knjiga)
    return sacuvaj_podatke(putanja_do_csv, podaci)

def obrisi_knjigu(putanja_do_csv, naslov):
    """Уклања књигу из библиотеке по наслову."""
    podaci = ucitaj_podatke(putanja_do_csv)
    nova_lista = [k for k in podaci if k.get("Наслов", "").lower() != naslov.lower()]
    if len(nova_lista) == len(podaci):
        return False
    return sacuvaj_podatke(putanja_do_csv, nova_lista)

def izmeni_knjigu(putanja_do_csv, naslov, nova_knjiga):
    """Измењује податке о књизи по наслову."""
    podaci = ucitaj_podatke(putanja_do_csv)
    izmenjeno = False
    
    # Обрада промена имена поља "Издавачи" -> "Издавач"
    if "Издавачи" in nova_knjiga and "Издавач" not in nova_knjiga:
        # Копирање вредности из поља "Издавачи" у поље "Издавач"
        nova_knjiga["Издавач"] = nova_knjiga["Издавачи"]
        # Уклањање поља "Издавачи" да не би изазвало грешку у CSV формату
        del nova_knjiga["Издавачи"]
    
    for i, knjiga in enumerate(podaci):
        if knjiga.get("Наслов", "").lower() == naslov.lower():
            for kljuc, vrednost in nova_knjiga.items():
                knjiga[kljuc] = vrednost
            izmenjeno = True
            break
    
    if izmenjeno:
        uspeh = sacuvaj_podatke(putanja_do_csv, podaci)
        if uspeh:
            # Ажурирамо регистар писаца након измене књиге
            azuriraj_registar_pisaca(podaci)
        return uspeh
    return False

def azuriraj_registar_pisaca(podaci):
    """Ажурира глобални регистар писаца након промена у подацима."""
    global pisci
    pisci = dobavi_sve_pisce(podaci)
    return pisci

def pretraga(putanja_do_csv, kriterijumi):
    """Претражује податке на основу критеријума."""
    podaci = ucitaj_podatke(putanja_do_csv)
    rezultat = []
    for knjiga in podaci:
        odgovara = True
        for kljuc, vrednost in kriterijumi.items():
            if vrednost and vrednost.lower() not in knjiga.get(kljuc, "").lower():
                odgovara = False
                break
        if odgovara:
            rezultat.append(knjiga)
    return rezultat

def pretraga_pozajmica(putanja_do_csv, naslov):
    """Претражује књиге по наслову да би нашао податке о позајмици."""
    podaci = ucitaj_podatke(putanja_do_csv)
    for knjiga in podaci:
        if knjiga.get("Наслов", "").lower() == naslov.lower():
            return {k: knjiga.get(k, "Не постоји податак") for k in ["Позајмљена", "Враћена", "Ко је позајмио"]}
    return None

# Иницијализуј глобалне променљиве модула одмах
inicijalizuj_podatke()

if __name__ == "__main__":
    putanja_do_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Biblioteka.csv')
    print("Модул за рад са библиотеком је успешно учитан.")
    print(f"Број жанрова: {len(zanr)}")
    print(f"Број издавача: {len(izdavac)}")
    print(f"Број типова повеза: {len(povez)}")
    print(f"Број регистрованих писаца: {len(pisci)}")