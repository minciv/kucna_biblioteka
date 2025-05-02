# -*- coding: utf-8 -*-
# @Аутор   : minciv
# @Фајл     : autocomplete_entry.py
# @Верзија  : 0.1.01.01.
# @Програм  : Windsurf
# @Опис     : Фајл са пољем за унос са аутоматским допуњавањем за Кућну Библиотеку

import tkinter as tk

class AutocompleteEntry(tk.Entry):
    """
    Класа за поље за унос текста са аутоматским допуњавањем.
    """
    def __init__(self, lista_vrednosti, *args, **kwargs):
        tk.Entry.__init__(self, *args, **kwargs)
        self.lista_vrednosti = lista_vrednosti
        self.var = self["textvariable"] if "textvariable" in kwargs else tk.StringVar()
        self["textvariable"] = self.var
        self.var.trace('w', self.changed)
        self.bind("<Return>", self.selection)
        self.bind("<Up>", self.move_up)
        self.bind("<Down>", self.move_down)
        self.bind("<FocusOut>", self.on_focus_out)
        
        self.listbox_up = False
        self.listbox = None

    def changed(self, name, index, mode):
        """Позива се када се промени текст у пољу."""
        if self.var.get() == '':
            if self.listbox_up:
                self.listbox.destroy()
                self.listbox_up = False
        else:
            words = self.comparison()
            if words:
                if not self.listbox_up:
                    self.listbox = tk.Listbox(width=self["width"], height=min(len(words), 7))
                    x = self.winfo_rootx()
                    y = self.winfo_rooty() + self.winfo_height()
                    self.listbox.place(x=x, y=y)
                    self.listbox_up = True
                    self.listbox.bind("<Button-1>", self.selection)
                    self.listbox.bind("<Return>", self.selection)
                
                self.listbox.delete(0, tk.END)
                for w in words:
                    self.listbox.insert(tk.END, w)
            else:
                if self.listbox_up:
                    self.listbox.destroy()
                    self.listbox_up = False

    def selection(self, event=None):
        """Позива се када се изабере ставка из листе."""
        if self.listbox_up:
            if self.listbox.curselection():
                self.var.set(self.listbox.get(self.listbox.curselection()))
            self.listbox.destroy()
            self.listbox_up = False
            self.icursor(tk.END)

    def move_up(self, event=None):
        """Помера селекцију на горе у листи."""
        if self.listbox_up:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]
                
            if index != '0':
                self.listbox.selection_clear(first=index)
                index = str(int(index) - 1)
                self.listbox.see(index)
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)

    def move_down(self, event=None):
        """Помера селекцију на доле у листи."""
        if self.listbox_up:
            if self.listbox.curselection() == ():
                index = '-1'
            else:
                index = self.listbox.curselection()[0]
                
            if index != tk.END:
                self.listbox.selection_clear(first=index)
                index = str(int(index) + 1)
                self.listbox.see(index)
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)

    def comparison(self):
        """Пореди тренутни текст са листом вредности."""
        pattern = self.var.get().lower()
        return [w for w in self.lista_vrednosti if pattern in w.lower()]

    def on_focus_out(self, event=None):
        """Позива се када поље изгуби фокус."""
        if self.listbox_up:
            # Дајемо мало времена за клик на листу пре него што је уништимо
            self.after(100, self.destroy_if_exists)

    def destroy_if_exists(self):
        """Уништава листу ако још увек постоји."""
        if self.listbox_up and not self.listbox.winfo_ismapped():
            self.listbox.destroy()
            self.listbox_up = False
