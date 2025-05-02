import csv

# Функција за учитавање података из CSV фајла
def ucitaj_podatke(put_do_bibcsv):
    # Учитава податке о књигама из CSV фајла
    biblioteka_podaci = []
    try:
        with open(put_do_bibcsv, 'r', encoding='utf-8') as fajl:
            reader = csv.DictReader(fajl)
            for red in reader:
                biblioteka_podaci.append(red)
    except FileNotFoundError:
        print(f"Грешка: Фајл '{put_do_bibcsv}' није пронађен.")
    return biblioteka_podaci

def pronadji_i_stampaj(biblioteka_podaci, kljuc, vrednost, sadrzi=False):
    pronadjene_knjige = False
    for knjiga in biblioteka_podaci:
        vrednost_knjige = knjiga.get(kljuc, "")
        if (sadrzi and vrednost.lower() in vrednost_knjige.lower()) or (not sadrzi and vrednost_knjige == vrednost):
            print("\nПронађена књига:")
            for kljuc, vrednost in knjiga.items():
                print(f"{kljuc}: {vrednost}")
            pronadjene_knjige = True
    return pronadjene_knjige

def pretraga_pozajmica(biblioteka_podaci, naslov):
    for knjiga in biblioteka_podaci:
        if knjiga.get("Наслов", "").lower() == naslov.lower():
            return {
                "Позајмљена": knjiga.get("Позајмљена", "Нема података"),
                "Враћена": knjiga.get("Враћена", "Нема података"),
                "Ко је позајмио": knjiga.get("Ко је позајмио", "Нема података")
            }
    return None
