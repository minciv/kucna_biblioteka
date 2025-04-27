# -*- coding: utf-8 -*-
# @Аутор   : minciv
# @Фајл     : backup_utils.py
# @Верзија  : 0.0.01.02.
# @Програм  : Windsurf
# @Опис     : Фајл за управљање резервним копијама за Кућну Библиотеку

import os
import shutil
import datetime
import glob
import re

# Конфигурација
# Максималан број резервних копија CSV фајлова
MAX_BACKUPS = 10  # Може се променити по потреби

def ocisti_stare_backup_fajlove(putanja_do_csv, max_backups=MAX_BACKUPS):
    """
    Брише најстарије backup фајлове ако их има више од дозвољеног броја.
    :param putanja_do_csv: Путања до главног CSV фајла
    :param max_backups: Максималан број backup фајлова који се чувају
    """
    # Проналазимо све бацкуп фајлове
    pattern = f"{putanja_do_csv}.backup_*"
    backup_fajlovi = glob.glob(pattern)
    
    # Сортирамо по времену модификације (најстарији први)
    backup_fajlovi.sort(key=os.path.getmtime)
    
    # Број фајлова које треба обрисати
    број_за_брисање = max(0, len(backup_fajlovi) - max_backups)
    
    # Бришемо најстарије фајлове
    for i in range(број_за_брисање):
        try:
            os.remove(backup_fajlovi[i])
            print(f"[INFO] Обрисан стари бацкуп: {backup_fajlovi[i]}")
        except Exception as e:
            print(f"[ERROR] Грешка при брисању бацкуп фајла {backup_fajlovi[i]}: {e}")

def napravi_backup(putanja_do_csv, max_backups=MAX_BACKUPS):
    """
    Прави резервну копију CSV фајла и аутоматски брише најстарије ако их има више од MAX_BACKUPS.
    :param putanja_do_csv: Путања до главног CSV фајла
    :param max_backups: Максималан број backup фајлова који се чувају
    :return: Путања до новог backup фајла
    """
    if not os.path.exists(putanja_do_csv):
        return False
    
    # Правимо нови бацкуп
    vreme = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_putanja = f"{putanja_do_csv}.backup_{vreme}"
    shutil.copy2(putanja_do_csv, backup_putanja)
    
    # Чистимо старе бацкуп фајлове
    ocisti_stare_backup_fajlove(putanja_do_csv, max_backups)
    
    return backup_putanja

# Пример употребе: позвати napravi_backup(putanja_do_csv, max_backups=10) пре sacuvaj_podatke или других измена.
