# -*- coding: utf-8 -*-
# @Аутор    : minciv
# @Фајл     : Biblioteka.py
# @Верзија  : 0.2.0
# @Програм  : Windsurf
# @Опис     : Датотека за управљање подацима о књигама

import os
import csv
from typing import List, Dict, Optional
from logger import get_logger
from config import CSV_COLUMNS, DEFAULT_DB_PATH

logger = get_logger(__name__)

# Иницијализација глобалних променљивих
zanr: List[str] = []
izdavac: List[str] = []
povez: List[str] = []
pisci: List[str] = []

def ucitaj_podatke(putanja_do_csv: str = DEFAULT_DB_PATH) -> List[Dict[str, str]]:
    """Učitava podatke iz CSV fajla sa poboljšanim rukovanjem greškama."""
    if not os.path.exists(putanja_do_csv):
        logger.error(f"Fajl nije pronađen: {putanja_do_csv}")
        return []
        
    try:
        with open(putanja_do_csv, 'r', encoding='utf-8') as csvfile:
            # Prvo pročitaj zaglavlje da proverimo kolone
            first_line = csvfile.readline().strip()
            csvfile.seek(0)  # Vrati se na početak fajla
            
            # Proveri da li je fajl prazan
            if not first_line:
                logger.error(f"CSV fajl je prazan: {putanja_do_csv}")
                return []
                
            reader = csv.DictReader(csvfile)
            
            # Proveri da li postoje sva zaglavlja
            if not reader.fieldnames:
                logger.error(f"CSV fajl nema zaglavlja: {putanja_do_csv}")
                return []
                
            # Proveri da li postoje sve obavezne kolone
            missing_columns = [col for col in CSV_COLUMNS if col not in reader.fieldnames]
            if missing_columns:
                logger.error(f"Nedostaju obavezne kolone u CSV fajlu: {putanja_do_csv}")
                logger.error(f"Nedostajuće kolone: {', '.join(missing_columns)}")
                return []
                
            # Učitaj podatke i proveri validnost
            data = []
            for i, row in enumerate(reader, start=2):  # Start=2 jer je prva linija zaglavlje
                # Proveri da li red ima sve potrebne kolone
                if all(col in row for col in CSV_COLUMNS):
                    data.append(row)
                else:
                    logger.warning(f"Red {i} nema sve potrebne kolone i biće preskočen")
            
            logger.info(f"Uspešno učitano {len(data)} zapisa iz {putanja_do_csv}")
            return data
            
    except UnicodeDecodeError:
        logger.error(f"Problem sa kodiranjem fajla. Pokušaj sa drugim encoding-om: {putanja_do_csv}")
        # Pokušaj sa drugim encoding-om
        try:
            with open(putanja_do_csv, 'r', encoding='cp1252') as csvfile:
                reader = csv.DictReader(csvfile)
                return list(reader)
        except Exception:
            logger.exception(f"Nije moguće pročitati fajl ni sa alternativnim encoding-om")
            return []
    except csv.Error as e:
        logger.error(f"CSV greška: {e}")
        return []
    except Exception as e:
        logger.exception(f"Neočekivana greška pri čitanju fajla: {e}")
        return []

def dobavi_sve_pisce(podaci: List[Dict[str, str]]) -> List[str]:
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

def podeli_pisce(pisci_text: str) -> List[str]:
    """Дели текст писаца раздвојен са ';' у листу писаца."""
    if not pisci_text:
        return []
    return [p.strip() for p in pisci_text.split(';') if p.strip()]

def inicijalizuj_podatke(putanja_do_csv: Optional[str] = None) -> Dict[str, List[str]]:
    """Иницијализује глобалне променљиве на основу података из CSV фајла."""
    global zanr, izdavac, povez, pisci

    # Подразумевана путања до CSV фајла
    putanja_do_csv = putanja_do_csv or DEFAULT_DB_PATH

    podaci = ucitaj_podatke(putanja_do_csv)

    # Помоћна функција за издвајање јединствених вредности из колоне
    def izdvoji_jedinstvene_vrednosti(kolona: str) -> List[str]:
        return sorted({row.get(kolona, "").strip() for row in podaci if row.get(kolona, "").strip()})

    zanr = izdvoji_jedinstvene_vrednosti("Жанр")
    povez = izdvoji_jedinstvene_vrednosti("Повез")

    # Обрада издавача
    izdavac_set = set()
    for row in podaci:
        for kolona in ["Издавачи", "Издавач"]:
            if row.get(kolona, "").strip():
                izdavac_set.update(map(str.strip, row[kolona].split(";")))
    izdavac = sorted(izdavac_set)

    # Креирање регистра писаца
    pisci = dobavi_sve_pisce(podaci)

    return {'zanr': zanr, 'izdavac': izdavac, 'povez': povez, 'pisci': pisci}

def sacuvaj_podatke(putanja_do_csv: str, podaci: List[Dict[str, str]]) -> bool:
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
        logger.exception(f"Greška pri pisanju u fajl: {e}")
        return False

def dodaj_knjigu(putanja_do_csv: str, nova_knjiga: Dict[str, str]) -> bool:
    """Додаје нову књигу у библиотеку."""
    podaci = ucitaj_podatke(putanja_do_csv)
    nova_knjiga["Редни број"] = str(len(podaci) + 1)
    podaci.append(nova_knjiga)
    return sacuvaj_podatke(putanja_do_csv, podaci)

def obrisi_knjigu(putanja_do_csv: str, naslov: str) -> bool:
    """Уклања књигу из библиотеке по наслову."""
    podaci = ucitaj_podatke(putanja_do_csv)
    nova_lista = [k for k in podaci if k.get("Наслов", "").lower() != naslov.lower()]
    if len(nova_lista) == len(podaci):
        return False
    return sacuvaj_podatke(putanja_do_csv, nova_lista)

def izmeni_knjigu(putanja_do_csv: str, naslov: str, nova_knjiga: Dict[str, str]) -> bool:
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

def azuriraj_registar_pisaca(podaci: List[Dict[str, str]]) -> List[str]:
    """Ажурира глобални регистар писаца након промена у подацима."""
    global pisci
    pisci = dobavi_sve_pisce(podaci)
    return pisci

def pretraga(putanja_do_csv: str, kriterijumi: Dict[str, str]) -> List[Dict[str, str]]:
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

def pretraga_pozajmica(putanja_do_csv: str, naslov: str) -> Optional[Dict[str, str]]:
    """Претражује књиге по наслову да би нашао податке о позајмици."""
    podaci = ucitaj_podatke(putanja_do_csv)
    for knjiga in podaci:
        if knjiga.get("Наслов", "").lower() == naslov.lower():
            return {k: knjiga.get(k, "Не постоји податак") for k in ["Позајмљена", "Враћена", "Ко је позајмио", "Датум позајмице", "Датум враћања", "Напомена о позајмици"]}
    return None

def pozajmi_knjigu(putanja_do_csv: str, naslov: str, ko_pozajmljuje: str, datum_pozajmice=None, datum_vracanja=None, napomena=None) -> bool:
    """Позајмљује књигу по наслову."""
    podaci = ucitaj_podatke(putanja_do_csv)
    for i, knjiga in enumerate(podaci):
        if knjiga.get("Наслов", "").lower() == naslov.lower():
            # Провери да ли је књига већ позајмљена
            if knjiga.get("Позајмљена", "") == "Да" and knjiga.get("Враћена", "") != "Да":
                logger.error(f"Knjiga '{naslov}' je već pozajmljena.")
                return False
                
            # Постави податке о позајмици
            podaci[i]["Позајмљена"] = "Да"
            podaci[i]["Враћена"] = ""
            podaci[i]["Ко је позајмио"] = ko_pozajmljuje
            
            # Додатни подаци
            if datum_pozajmice:
                podaci[i]["Датум позајмице"] = datum_pozajmice.strftime("%Y-%m-%d")
            else:
                from datetime import date
                podaci[i]["Датум позајмице"] = date.today().strftime("%Y-%m-%d")
                
            if datum_vracanja:
                podaci[i]["Датум враћања"] = datum_vracanja.strftime("%Y-%m-%d")
            else:
                podaci[i]["Датум враћања"] = ""
                
            if napomena:
                podaci[i]["Напомена о позајмици"] = napomena
            
            return sacuvaj_podatke(putanja_do_csv, podaci)
    
    logger.error(f"Knjiga '{naslov}' nije pronađena.")
    return False

def vrati_knjigu(putanja_do_csv: str, naslov: str) -> bool:
    """Враћа позајмљену књигу по наслову."""
    podaci = ucitaj_podatke(putanja_do_csv)
    for i, knjiga in enumerate(podaci):
        if knjiga.get("Наслов", "").lower() == naslov.lower():
            # Провери да ли је књига позајмљена
            if knjiga.get("Позајмљена", "") != "Да" or knjiga.get("Враћена", "") == "Да":
                logger.error(f"Knjiga '{naslov}' nije pozajmljena.")
                return False
                
            # Постави податке о враћању
            podaci[i]["Враћена"] = "Да"
            
            # Додај датум враћања
            from datetime import date
            podaci[i]["Датум враћања"] = date.today().strftime("%Y-%m-%d")
            
            return sacuvaj_podatke(putanja_do_csv, podaci)
    
    logger.error(f"Knjiga '{naslov}' nije pronađena.")
    return False

# Иницијализуј глобалне променљиве модула одмах
inicijalizuj_podatke()

if __name__ == "__main__":
    putanja_do_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Biblioteka.csv')
    print("Модул за рад са библиотеком је успешно учитан.")
    inicijalizuj_podatke()
    print(f"Број жанрова: {len(zanr)}")
    print(f"Број издавача: {len(izdavac)}")
    print(f"Број типова повеза: {len(povez)}")
    print(f"Број регистрованих писаца: {len(pisci)}")