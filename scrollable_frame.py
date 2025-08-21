# -*- coding: utf-8 -*-
# @Аутор    : minciv
# @Фајл     : scrollable_frame.py
# @Верзија  : 0.2.0
# @Програм  : Windsurf
# @Опис     : Датотека за управљање клизачима у корисничком интерфејсу

# Увозимо потребне модуле
import tkinter as tk
from tkinter import ttk

# Класа за клизач
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, height=100, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, height=height, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        # Експлицитна конфигурација за колоне и редове у унутрашњем фрејму
        self.scrollable_frame.grid_columnconfigure(0, weight=0)  # Колона за дугмад
        self.scrollable_frame.grid_columnconfigure(1, weight=1)  # Колона за унос
        
        # Постављање редова (довољно за типичан број елемената)
        for i in range(15):
            self.scrollable_frame.grid_rowconfigure(i, weight=0)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # Функција за враћање унутрашњег фрејма
    def get_frame(self):
        return self.scrollable_frame
