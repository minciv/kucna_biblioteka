# -*- coding: utf-8 -*-
# @Аутор   : minciv
# @Фајл     : kucna_biblioteka.py
# @Верзија  : 0.1.01.01.
# @Програм  : Windsurf
# @Опис     : Главна датотека за покретање програма Кућна Библиотека

import os
from biblioteka_gui import main
import Biblioteka as bib

if __name__ == "__main__":
    try:
        # Релативна путања до CSV фајла (у истом директоријуму)
        putanja_do_bcsv = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Biblioteka.csv')
        
        # Провери да ли датотека постоји
        if not os.path.exists(putanja_do_bcsv):
            print(f"Упозорење: CSV фајл није пронађен на путањи: {putanja_do_bcsv}")
        
        # Покрени главну апликацију
        main(putanja_do_bcsv)
    except Exception as e:
        import logging
        from logging.handlers import RotatingFileHandler
        # Конфигурација ротирајућег логовања (чувај до 5 лог фајлова, само INFO и више)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler('biblioteka.log', maxBytes=20000, backupCount=5, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.exception("Покретање апликације није успело:")
        print(f"Грешка при покретању апликације: {e}")
