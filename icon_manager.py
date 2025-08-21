#!/usr/bin/env python3
# -*- coding : utf-8 -*-
# @Аутор     : minciv
# @Фајл      : icon_manager.py
# @Верзија   : 0.2.0
# @Програм   : Windsurf
# @Опис      : Менаџер икона за програм Кућна Библиотека

# Увозимо потребне модуле
import os
import tkinter as tk
from PIL import Image, ImageTk

# Класа за управљање иконама
class IconManager:
    """Класа која управља иконама апликације"""
    
    def __init__(self, icons_dir=None):
        """Иницијализује менаџер икона"""
        if icons_dir is None:
            # Default path for icons directory
            self.icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
        else:
            self.icons_dir = icons_dir
        
        self.icons = {}  # Кеш за иконе
        self.icon_size = (16, 16)  # Подразумевана величина иконе
        self.icons_loaded = False  # Пратимо да ли су иконе учитане
    
    # Метод за учитавање иконица
    def load_icons(self, root=None):
        """Учитава иконе из директоријума. Потребан је root објекат Tkinter-а"""
        # Већ учитано?
        if self.icons_loaded:
            return self.icons
            
        # Проверавамо да ли постоји директоријум
        if not os.path.exists(self.icons_dir):
            print(f"ГРЕШКА: Директоријум са иконама не постоји: {self.icons_dir}")
            return self.icons
        
        # Мапа кључева икона према именима фајлова без екстензије
        icon_names = [
            'all_books', 'search_books', 'add_book', 'edit_book', 'delete_book',
            'search_loans', 'all_authors', 'statistics', 'settings', 'exit',
            'export_json', 'import_json', 'export_excel', 'import_excel',
            'back', 'back_to_main', 'search_author_books'
        ]
        
        # Учитавамо све PNG иконе
        for name in icon_names:
            icon_path = os.path.join(self.icons_dir, f"{name}.png")
            if os.path.exists(icon_path):
                try:
                    # Учитавамо и ресајзујемо икону
                    img = Image.open(icon_path)
                    img = img.resize(self.icon_size, Image.LANCZOS)
                    photo_img = ImageTk.PhotoImage(img, master=root)
                    self.icons[name] = photo_img
                except Exception as e:
                    print(f"ГРЕШКА: Не могу да учитам икону {name}: {e}")
        
        self.icons_loaded = True
        return self.icons
    
    # Метод за враћање иконе по кључу
    def get_icon(self, key, root=None):
        """Враћа икону за дати кључ или None ако не постоји"""
        # Ако иконе нису учитане, учитај их сада
        if not self.icons_loaded and root is not None:
            self.load_icons(root)
        return self.icons.get(key)
    
    # Метод за враћање свих иконица
    def get_all_icons(self, root=None):
        """Враћа све иконе"""
        # Ако иконе нису учитане, учитај их сада
        if not self.icons_loaded and root is not None:
            self.load_icons(root)
        return self.icons
    
    # Метод за постављање величине иконица
    def set_icon_size(self, width, height, root=None):
        """Поставља величину икона и поново учитава иконе"""
        self.icon_size = (width, height)
        self.icons_loaded = False
        if root is not None:
            self.load_icons(root)

# Глобална инстанца менаџера икона
ICON_MANAGER = None

# Функција за иницијализацију менаџера икона
def initialize_icons(icons_dir=None):
    """Иницијализира глобалну инстанцу менаџера икона"""
    global ICON_MANAGER
    if ICON_MANAGER is None:
        # Ако icons_dir је None, IconManager će користити подразумевану путању
        ICON_MANAGER = IconManager(icons_dir)
        print(f"Icon Manager initialized with path: {ICON_MANAGER.icons_dir}")
    return ICON_MANAGER

# Функција за враћање глобалне инстанце менаџера икона
def get_icon_manager():
    """Враћа глобалну инстанцу менаџера икона"""
    global ICON_MANAGER
    if ICON_MANAGER is None:
        initialize_icons()
    return ICON_MANAGER
