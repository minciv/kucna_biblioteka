# -*- coding: utf-8 -*-
# @Author  : minciv
# @File    : biblioteka_gui.py
# @Software: Windsurf
# @Description: Датотека за покретање GUI за Кућну Библиотеку

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import Biblioteka as bib
from scrollable_frame import ScrollableFrame
import os
import json
from translations import TRANSLATIONS, ICONS
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except ImportError:
    Figure = None

# Путања до фајла са подешавањима
SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')

# Подразумевана подешавања
DEFAULT_SETTINGS = {
    'theme': 'clam',
    'language': 'sr_CYRL',
    'show_icons': True
}

# Увозимо податке из модула Библиотека, или креирамо празне листе ако не постоје
try:
    from Biblioteka import zanr, izdavac, povez, pisci
except ImportError:
    # Ако нешто недостаје, иницијализујемо празне листе
    zanr = []
    izdavac = []
    povez = []
    pisci = []

# Увоз статистике
from statistika import (
    ukupno_knjiga, ukupno_auta, broj_zanrova, broj_serijala, broj_pozajmica,
    knjige_po_zanru, knjige_po_izdavacu, top_autori
)

# Ствара класу Библиотека
class BibliotekaGUI:
    def __init__(self, root, putanja):
        self.root = root
        self.root.title("Кућна Библиотека")
        self.putanja = putanja
        self.frame_stack = []
        self.current_frame = None
        # Креира главни контејнер
        self.container = tk.Frame(self.root)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=1)
        self.load_settings()
        style = ttk.Style()
        style.theme_use(self.settings.get('theme', DEFAULT_SETTINGS['theme']))
        self.setup_menu()
        self.setup_main_window()
        self.root.minsize(400, 300)
        # self.root.maxsize(800, 600)  # Allow unlimited expansion
        # Keyboard shortcuts
        self.root.bind_all("<Control-n>", lambda e: self.otvori_dodavanje())
        self.root.bind_all("<Control-s>", lambda e: self.save_current_form())  # Save shortcut

    def save_current_form(self):
        # Placeholder: implement if you want Ctrl+S to trigger save in current form
        pass
        self.root.bind_all("<Control-f>", lambda e: self.otvori_pretragu())
        self.root.bind_all("<Escape>", lambda e: self.go_back())

    # Поставља главни прозор са дугметима за различите акције.
    def setup_main_window(self):
        if hasattr(self, 'main_frame') and self.main_frame.winfo_exists():
            self.main_frame.destroy()
        # Уништава тренутни фрејм ако постоји    
        self.main_frame = tk.Frame(self.container)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        commands = [
            ("all_books", self.prikazi_knjige),
            ("search_books", self.otvori_pretragu),
            ("add_book", self.otvori_dodavanje),
            ("edit_book", self.otvori_izmenu),
            ("delete_book", self.otvori_brisanje),
            ("search_loans", self.otvori_pozajmice)
        ]
        
        # Додаје дугме за преглед писаца ако постоји регистар писаца
        if 'pisci' in globals() and pisci:
            commands.append(("all_authors", self.prikazi_sve_pisce))
        
        # Buttons with tooltips and shortcut info
        shortcuts = {self.otvori_dodavanje: "Ctrl+N", self.otvori_pretragu: "Ctrl+F", self.go_back: "Esc"}
        for i, (key, command) in enumerate(commands):
            label = self._get_label(key)
            btn = ttk.Button(self.main_frame, text=label, command=command)
            btn.grid(row=i, column=0, pady=5, padx=10, sticky="ew")
            sc = shortcuts.get(command)
            if sc:
                ToolTip(btn, f"{label} ({sc})")
        
        # Покажи главни фрејм само једном
        self.show_frame(self.main_frame)

    # Приказује све писце
    def prikazi_sve_pisce(self):
        """Приказује све писце из регистра."""
        if not hasattr(bib, 'pisci') or not bib.pisci:
            messagebox.showinfo("Информација", "Нема доступних писаца у регистру.")
            return
            
        frame = self.create_new_frame()
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        tk.Label(frame, text=self._get_label('authors_register'), font=("Helvetica", 14, "bold")).grid(row=0, column=0, pady=10)
        
        # Креира Listbox са клизачем
        list_frame = tk.Frame(frame)
        list_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        pisci_listbox = tk.Listbox(list_frame, width=40, height=15)
        pisci_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Повезује листу са клизачем
        pisci_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=pisci_listbox.yview)
        
        # Попуњава листу писцима
        for pisac in sorted(bib.pisci):
            pisci_listbox.insert(tk.END, pisac)
        
        # Додаје дугме за претрагу књига од изабраног писца
        def pretrazi_izabranog_pisca():
            selection = pisci_listbox.curselection()
            if selection:
                pisac = pisci_listbox.get(selection[0])
                self.pretrazi_po_piscu(pisac)
            else:
                messagebox.showinfo("Обавештење", "Најпре изаберите писца из листе.")
        
        btn = ttk.Button(frame, text=self._get_label('search_author_books'), command=pretrazi_izabranog_pisca)
        btn.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # Приказујемо само оквир са писцима
        self.show_frame(frame)

    # Приказује фрејм
    def show_frame(self, frame):
        """Приказује нови фрејм и сакрива тренутни."""
        try:
            # Сакрива тренутни фрејм ако постоји
            if self.current_frame and self.current_frame.winfo_exists():
                self.current_frame.grid_remove()
                
            # Приказује нови фрејм
            frame.grid(row=0, column=0, sticky="nsew")
            self.current_frame = frame
            
            # Додаје дугме "Назад" ако није главни прозор
            if frame != self.main_frame:
                self.add_back_button(frame)
                
            # Додаје фрејм у стек ако већ није додат
            if frame not in self.frame_stack:
                # Ако је главни фрејм, ресетујемо стек
                if frame == self.main_frame:
                    self.frame_stack = [frame]
                else:
                    self.frame_stack.append(frame)
            # Refresh menu to update Back item
            self.setup_menu()
        except tk.TclError as e:
            print(f"Грешка при приказивању фрејма: {e}")
            # Ако дође до грешке, враћа се на главни прозор
            self.frame_stack = []
            self.setup_main_window()

    # Додаје дугме "Назад" у фрејм
    def add_back_button(self, frame):
        # Проналази последњи ред у фрејму
        last_row = 0
        for child in frame.grid_slaves():
            last_row = max(last_row, child.grid_info()['row'])
        # Проверава да ли дугме "Назад" већ постоји
        back_button_exists = False
        for child in frame.grid_slaves():
            if isinstance(child, tk.Button) and child.cget("text") in [self._get_label('back')]:
                back_button_exists = True
                break
        # Ако дугме "Назад" не постоји, додаје ново
        if not back_button_exists:
            back_btn = tk.Button(frame, text=self._get_label('back'), command=self.go_back)
            back_btn.grid(row=last_row + 1, column=0, columnspan=2, pady=10, sticky="ew")

    # Враћа се на претходни фрејм
    def go_back(self):
        """Враћа се на претходни фрејм и уништава тренутни."""
        if len(self.frame_stack) > 1:
            try:
                # Уклањамо тренутни фрејм из стека
                current = self.frame_stack.pop()
                
                # Проверавамо да ли је тренутни фрејм и даље валидан
                try:
                    if current.winfo_exists():
                        current.destroy()
                except tk.TclError:
                    pass  # Ако фрејм више не постоји, идемо даље
                
                # Узимамо претходни фрејм из стека
                previous = self.frame_stack[-1]
                
                # Проверавамо да ли је претходни фрејм валидан
                try:
                    if previous.winfo_exists():
                        self.show_frame(previous)
                        return
                except tk.TclError:
                    pass  # Ако фрејм више не постоји, идемо на главни прозор
                
                # Ако се дође до овде, значи да претходни фрејм није валидан
                self.frame_stack = []
                self.setup_main_window()
            except (IndexError, Exception):
                # У случају било које грешке, враћамо се на главни прозор
                self.frame_stack = []
                self.setup_main_window()
        else:
            # Ако нема претходног фрејма, само приказујемо главни
            self.setup_main_window()

    # Додата помоћна функција за приказ у Разгранатом облику са клизачем
    def create_treeview_with_scrollbar(self, frame, columns, column_widths):
        # Креира табеларни приказ са клизачем
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)  # Подешавање висине редова
        
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col, width in zip(columns, column_widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, minwidth=50)
            
        # Додавање клизача
        scrollbar_y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar_x = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Постављање компоненти
        tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        return tree

    # Izmenjena funkcija prikazi_rezultate da koristi pomoćnu funkciju
    def prikazi_rezultate(self, rezultati):
        if not rezultati:
            messagebox.showinfo(self._get_label('information'), self._get_label('no_books_found'))
            return
        frame = self.create_new_frame()
        tree = self.create_treeview_with_scrollbar(frame, columns=("Наслов",), column_widths=(200,))
        for knjiga in rezultati:
            tree.insert("", "end", values=(knjiga["Наслов"],))
        tree.bind("<Double-1>", lambda event: self.prikazi_detalje_knjige(
            tree.item(tree.selection()[0], "values")[0], rezultati, frame) if tree.selection() else messagebox.showinfo(self._get_label('error'), self._get_label('no_book_selected'))
        )
        self.show_frame(frame)

    # Izmenjena funkcija prikazi_knjige da koristi pomoćnu funkciju i podržava više kolona
    def prikazi_knjige(self):
        podaci = bib.ucitaj_podatke(self.putanja)
        if not podaci:
            messagebox.showinfo(self._get_label('information'), self._get_label('no_books_found'))
            return
        frame = self.create_new_frame()
        columns = ("Наслов", "Писац", "Година издавања", "Доступност")
        column_widths = (200, 150, 100, 100)
        tree = self.create_treeview_with_scrollbar(frame, columns, column_widths)
        for knjiga in podaci:
            dostup = self._compute_availability(knjiga)
            tree.insert("", "end", values=(knjiga.get("Наслов",""), knjiga.get("Писац",""), knjiga.get("Година издавања",""), dostup))
        
        def on_double(event):
            sel = tree.selection()
            if not sel:
                messagebox.showinfo(self._get_label('error'), self._get_label('no_book_selected'))
                return
            values = tree.item(sel[0], "values")
            naslov, dostup = values[0], values[3]
            if dostup == "Није доступна":
                self._show_loan_details(naslov)
            else:
                self.prikazi_detalje_knjige(naslov, podaci, frame)
        
        def on_right_click(event):
            # Прво селектујемо ставку на којој је кликнуто
            item = tree.identify_row(event.y)
            if item:
                # Селектујемо ставку
                tree.selection_set(item)
                # Приказујемо контекстни мени
                self._show_context_menu(event, tree, podaci)
        
        tree.bind("<Double-1>", on_double)
        tree.bind("<Button-3>", on_right_click)  # Button-3 је десни клик
        self.show_frame(frame)

    # Приказује контекстни мени за књигу
    def _show_context_menu(self, event, tree, podaci):
        """Приказује контекстни мени на десни клик."""
        # Проверавамо да ли је изабрана књига
        sel = tree.selection()
        if not sel:
            return
        
        # Узимамо наслов изабране књиге
        values = tree.item(sel[0], "values")
        naslov = values[0]
        
        # Креирамо контекстни мени
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label=self._get_label('edit_book'), command=lambda: self.otvori_izmenu(naslov))
        context_menu.add_command(label=self._get_label('details'), command=lambda: self.prikazi_detalje_knjige(naslov, podaci, self.current_frame))
        
        # Приказујемо мени на позицији миша
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Обавезно уништавамо мени након затварања
            context_menu.grab_release()
    
    def on_right_click(event):
        # Прво селектујемо ставку на којој је кликнуто
        item = tree.identify_row(event.y)
        if item:
            # Селектујемо ставку
            tree.selection_set(item)
            # Приказујемо контекстни мени
            self._show_context_menu(event, tree, podaci)

    # Врши промену књиге из листе
    def otvori_izmenu(self, naslov_knjige=None):
        try:
            print("[DEBUG] Позвана је функција otvori_izmenu.")
            frame = self.create_new_frame()
            frame.grid_columnconfigure(1, weight=1)
            tk.Label(frame, text=self._get_label('enter_book_title_edit')).grid(row=0, column=0, pady=5)
            naslov_entry = tk.Entry(frame)
            naslov_entry.grid(row=1, column=0, pady=5)
            
            # Ако је прослеђен наслов књиге, попуњавамо поље
            if naslov_knjige:
                naslov_entry.insert(0, naslov_knjige)

            def pronadji():
                print(f"[DEBUG] Притиснуто дугме 'Пронађи'. Унет наслов: {naslov_entry.get()}")
                try:
                    # Ако је унет наслов, тражимо књигу
                    if naslov_entry.get():
                        knjiga = next((k for k in bib.ucitaj_podatke(self.putanja)
                                   if k.get("Наслов", "").lower() == naslov_entry.get().lower()), None)
                        if not knjiga:
                            print("[DEBUG] Књига није пронађена!")
                            messagebox.showerror(self._get_label('error'), self._get_label('book_not_found'))
                            return
                        print(f"[DEBUG] Пронађена књига: {knjiga}")
                        edit_frame = self.create_new_frame()
                        edit_frame.grid_columnconfigure(1, weight=1)
                        tk.Label(edit_frame, text=f"{self._get_label('edit_book_title')} {knjiga['Наслов']}", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
                        fields = ["Наслов", "Писац", "Година издавања", "Жанр", "Серијал", "Колекција", "Издавач", "ИСБН", "Повез", "Напомена", "Позајмљена", "Враћена", "Ко је позајмио"]
                        entries = {}
                        for i, field in enumerate(fields):
                            tk.Label(edit_frame, text=f"{field}:").grid(row=i+1, column=0, padx=5, pady=5)
                            if field == "Писац":
                                author_section = tk.LabelFrame(edit_frame, text=self._get_label('authors'), padx=2, pady=2)
                                author_section.grid(row=i+1, column=1, padx=5, pady=5, sticky="nsew", columnspan=2)
                                edit_frame.grid_rowconfigure(i+1, weight=1)
                                edit_frame.grid_columnconfigure(1, weight=1)
                                author_section.grid_rowconfigure(0, weight=1)
                                author_section.grid_columnconfigure(0, weight=1)

                                # Корисничко поље за ауторе
                                scrollable_authors = ScrollableFrame(author_section, height=120)
                                scrollable_authors.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
                                authors_container = scrollable_authors.get_frame()
                                authors_container.grid_columnconfigure(1, weight=1)
                                entries_authors = []
                                # Додајемо новог аутора
                                def add_author_field_edit(name=""):
                                    row = len(entries_authors)
                                    btn_remove = ttk.Button(authors_container, text="-", width=2, command=lambda r=row: remove_author_field_edit(r))
                                    btn_remove.grid(row=row, column=0, padx=2, pady=2, sticky="nw")
                                    entry = ttk.Combobox(authors_container, values=pisci, width=25)
                                    entry.grid(row=row, column=1, padx=2, pady=2, sticky="ew")
                                    entry.insert(0, name)
                                    authors_container.grid_rowconfigure(row, weight=0)
                                    entries_authors.append(entry)
                                # Уклањање аутора
                                def remove_author_field_edit(row):
                                    if 0 <= row < len(entries_authors):
                                        entries_authors[row].destroy()
                                        entries_authors.pop(row)
                                        for i, entry in enumerate(entries_authors):
                                            btn = None
                                            for widget in authors_container.grid_slaves(row=i, column=0):
                                                if isinstance(widget, ttk.Button):
                                                    btn = widget
                                                    break
                                            if btn:
                                                btn.grid(row=i, column=0, padx=2, pady=2, sticky="nw")
                                            entry.grid(row=i, column=1, padx=2, pady=2, sticky="ew")
                                    else:
                                        print(f"[DEBUG] Покушај брисања невалидног аутора: {row}")

                                # Користимо podeli_pisce функцију за правилно раздвајање писаца
                                existing = knjiga.get("Писац", "")
                                existing_authors = bib.podeli_pisce(existing) if hasattr(bib, 'podeli_pisce') and isinstance(existing, str) else []
                                        
                                # Додај поље за сваког аутора посебно
                                for name in existing_authors:
                                    add_author_field_edit(name)
                                if not existing_authors:
                                    add_author_field_edit()

                                # Додајемо поље за додавање новог аутора
                                add_author_frame = tk.Frame(author_section)
                                add_author_frame.grid(row=1, column=0, sticky="ew", pady=(5,0))
                                add_author_frame.grid_columnconfigure(0, weight=1)
                                new_author_entry = ttk.Combobox(add_author_frame, values=pisci, width=25)
                                new_author_entry.grid(row=0, column=0, padx=2, sticky="ew")

                                # Додајемо новог аутора из корисничког поља
                                def add_new_author_from_entry():
                                    name = new_author_entry.get().strip()
                                    if name:
                                        add_author_field_edit(name)
                                        new_author_entry.delete(0, tk.END)

                                btn_add = ttk.Button(add_author_frame, text="+", width=2, command=add_new_author_from_entry)
                                btn_add.grid(row=0, column=1, padx=2)
                                # Ово поље ће садржати све уносе аутора
                                # Чувамо листу поља за ауторе
                                entries["Писац"] = entries_authors
                            elif field == "Жанр":
                                entry = ttk.Combobox(edit_frame, values=zanr, width=25)
                                entry.grid(row=i+1, column=1, padx=5, pady=5, sticky="ew")
                                entry.set(knjiga.get(field, ""))
                                entries[field] = entry
                            elif field == "Издавач":
                                entry = ttk.Combobox(edit_frame, values=izdavac, width=25)
                                entry.grid(row=i+1, column=1, padx=5, pady=5, sticky="ew")
                                entry.set(knjiga.get(field, ""))
                                entries[field] = entry
                            elif field == "Повез":
                                entry = ttk.Combobox(edit_frame, values=povez, width=25)
                                entry.grid(row=i+1, column=1, padx=5, pady=5, sticky="ew")
                                entry.set(knjiga.get(field, ""))
                                entries[field] = entry
                            else:
                                entry = tk.Entry(edit_frame)
                                entry.grid(row=i+1, column=1, padx=5, pady=5, sticky="ew")
                                entry.insert(0, knjiga.get(field, ""))
                                entries[field] = entry
                        def sacuvaj_izmenu():
                            print("[DEBUG] Притиснуто дугме 'Сачувај измене'.")
                            nova_knjiga = {}
                            for field in fields:
                                if field == "Писац":
                                    # Сви аутори се чувају одвојено, сваки у свом пољу
                                    # Прикупи све ауторе из појединачних поља и споји их са тачка-запетом
                                    authors = [e.get() for e in entries_authors if e.get().strip()]
                                    nova_knjiga[field] = "; ".join(authors)
                                elif field in ["Жанр", "Издавач"]:
                                    val = entries[field].get() if hasattr(entries[field], 'get') else entries[field].get()
                                    nova_knjiga[field] = val
                                elif hasattr(entries[field], 'get'):
                                    nova_knjiga[field] = entries[field].get()
                                else:
                                    nova_knjiga[field] = entries[field]
                            uspeh = bib.izmeni_knjigu(self.putanja, knjiga['Наслов'], nova_knjiga)
                            if uspeh:
                                print("[DEBUG] Књига успешно измењена!")
                                if hasattr(bib, 'inicijalizuj_podatke'):
                                    azurirani_podaci = bib.inicijalizuj_podatke(self.putanja)
                                    global zanr, izdavac, pisci
                                    zanr = azurirani_podaci['zanr']
                                    izdavac = azurirani_podaci['izdavac']
                                    pisci = azurirani_podaci['pisci']
                                messagebox.showinfo(self._get_label('success'), self._get_label('book_edited'))
                                self.go_back()
                            else:
                                print("[DEBUG] Грешка при измени књиге!")
                                messagebox.showerror(self._get_label('error'), self._get_label('error_editing_book'))
                        btn_save = tk.Button(edit_frame, text=self._get_label('save_changes'), command=sacuvaj_izmenu)
                        btn_save.grid(row=len(fields)+1, column=0, columnspan=3, pady=10, sticky="ew")
                        self.show_frame(edit_frame)

                except Exception as ex:
                    print(f"[DEBUG] Изузетак у pronadji: {ex}")
                    messagebox.showerror(self._get_label('error'), f"Дошло је до грешке: {ex}")

            btn_pronadji = tk.Button(frame, text=self._get_label('find'), command=pronadji)
            btn_pronadji.grid(row=2, column=0, pady=5)
            self.show_frame(frame)
            
            # Ако је прослеђен наслов књиге, одмах покрећемо претрагу
            if naslov_knjige:
                pronadji()
        except Exception as ex:
            print(f"[DEBUG] Изузетак у otvori_izmenu: {ex}")
            messagebox.showerror(self._get_label('error'), f"Дошло је до грешке: {ex}")

    # Отвара форму за брисање књиге
    def otvori_brisanje(self):
        frame = self.create_new_frame()
        tk.Label(frame, text=self._get_label('enter_book_title_delete')).grid(row=0, column=0, pady=5)
        unos = tk.Entry(frame)
        unos.grid(row=1, column=0, pady=5)
        def obrisi():
            # Брише књигу са датим насловом.
            naslov = unos.get()
            if naslov:
                odgovor = messagebox.askyesno(self._get_label('confirmation'), f"Да ли сте сигурни да желите да обришете књигу '{naslov}'?")
                if odgovor and bib.obrisi_knjigu(self.putanja, naslov):
                    messagebox.showinfo(self._get_label('success'), self._get_label('book_deleted'))
                    self.go_back()
                else:
                    messagebox.showerror(self._get_label('error'), self._get_label('book_not_found'))
        tk.Button(frame, text=self._get_label('delete'), command=obrisi).grid(row=2, column=0, pady=5)
        self.show_frame(frame)
    
    # Отвара форму за претрагу књига
    def otvori_pretragu(self):
        frame = self.create_new_frame()
        tk.Label(frame, text=self._get_label('search_options')).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Освежавамо листе писаца, жанрова и издавача
        global zanr, izdavac, pisci
        try:
            podaci = bib.inicijalizuj_podatke(self.putanja)
            zanr = podaci['zanr']
            izdavac = podaci['izdavac']
            pisci = podaci['pisci']
        except Exception as e:
            print(f"[DEBUG] Грешка при учитавању података: {e}")
        
        # Креира поља за претрагу - искључујемо Повез из критеријума
        fields = ["Наслов", "Писац", "Година издавања", "Жанр", "Издавач"]
        entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(frame, text=f"{field}:").grid(row=i+1, column=0, padx=5, pady=5, sticky="e")
            if field == "Писац":
                # За писце користимо комбобокс
                entry = ttk.Combobox(frame, values=pisci, width=25)
            elif field == "Жанр":
                entry = ttk.Combobox(frame, values=zanr, width=25)
            elif field == "Издавач":
                entry = ttk.Combobox(frame, values=izdavac, width=25)
            elif field == "Повез":
                entry = ttk.Combobox(frame, values=povez, width=25)
            else:
                entry = tk.Entry(frame, width=25)
            entry.grid(row=i+1, column=1, padx=5, pady=5, sticky="w")
            entries[field] = entry
        
        # Дугме за претрагу
        def pretrazi():
            criteria = {}
            for field, entry in entries.items():
                value = entry.get().strip() if hasattr(entry, 'get') else ""
                if value:
                    criteria[field] = value
            if not criteria:
                messagebox.showinfo(self._get_label('information'), self._get_label('enter_search_criteria'))
                return
            rezultati = bib.pretraga(self.putanja, criteria)
            self.prikazi_rezultate(rezultati)
        
        tk.Button(frame, text=self._get_label('search'), command=pretrazi).grid(row=len(fields)+1, column=0, columnspan=2, pady=10)
        self.show_frame(frame)
    
    # Приказује детаље о књизи
    def prikazi_detalje_knjige(self, naslov, podaci, parent_frame):
        knjiga = next((k for k in podaci if k["Наслов"] == naslov), None)
        if not knjiga:
            messagebox.showinfo(self._get_label('error'), self._get_label('book_not_found'))
            return
        # Уништава тренутни фрејм
        details_frame = self.create_new_frame()
        tk.Label(details_frame, text=f"{self._get_label('details')} {naslov}", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        text_details = tk.Text(details_frame, wrap=tk.WORD, width=40, height=10)
        text_details.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        details = ""
        # Приказује детаље о књизи
        for kljuc, vrednost in knjiga.items():
            if kljuc == "Писац":
                autori = bib.podeli_pisce(vrednost) if hasattr(bib, 'podeli_pisce') else vrednost.split(';')
                autori = [autor.strip() for autor in autori if autor.strip()]
                if len(autori) > 1:
                    details += f"{kljuc}:\n"
                    for autor in autori:
                        details += f"  - {autor}\n"
                else:
                    details += f"{kljuc}: {vrednost}\n"
            else:
                details += f"{kljuc}: {vrednost}\n"
        text_details.insert(tk.END, details)
        text_details.config(state=tk.DISABLED)
        
        # Ако књига има више писаца, додајемо дугме за претрагу по писцу
        if "Писац" in knjiga:
            autori = bib.podeli_pisce(knjiga["Писац"]) if hasattr(bib, 'podeli_pisce') else [a.strip() for a in knjiga["Писац"].split(';')]
            autori = [a for a in autori if a.strip()]  # Уклањамо празне вредности

            if len(autori) > 0:
                # Креира оквир за дугмад
                buttons_frame = tk.Frame(details_frame)
                buttons_frame.grid(row=2, column=0, columnspan=2, pady=5)
                tk.Label(buttons_frame, text=self._get_label('search_author_books_this'), font=("Helvetica", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

                # Одређујемо број колона за дугмад (максимално 5 дугмета по реду)
                max_buttons_per_row = 5

                # За сваког писца додаје дугме
                for i, autor in enumerate(autori):
                    if autor.strip():
                        # Израчунава ред и колону за дугме
                        row = (i // max_buttons_per_row) + 1
                        col = i % max_buttons_per_row

                        pisac_btn = tk.Button(buttons_frame, text=autor,
                                             command=lambda a=autor: self.pretrazi_po_piscu(a))
                        pisac_btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

                # Конфигуришемо колоне да буду једнаке ширине
                for i in range(min(max_buttons_per_row, len(autori))):
                    buttons_frame.grid_columnconfigure(i, weight=1)
        
        tk.Button(details_frame, text=self._get_label('back'), command=self.go_back).grid(row=3, column=0, columnspan=2, pady=10)
        self.show_frame(details_frame)

    # Претрага по писцу
    def pretrazi_po_piscu(self, pisac):
        """Претражује књиге одређеног писца."""
        kriterijumi = {"Писац": pisac}
        rezultati = bib.pretraga(self.putanja, kriterijumi)
        if rezultati:
            self.prikazi_rezultate(rezultati)
        else:
            messagebox.showinfo(self._get_label('information'), f"Нема пронађених књига за писца: {pisac}")

    # Креира нови фрејм
    def create_new_frame(self):
        frame = tk.Frame(self.container)
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        return frame

    def load_settings(self):
        """Учита и/или креира фајл са подешавањима"""
        path = SETTINGS_PATH
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_SETTINGS, f, ensure_ascii=False, indent=4)
            settings = DEFAULT_SETTINGS.copy()
        else:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except:
                settings = DEFAULT_SETTINGS.copy()
        self.settings = settings

    def save_settings(self):
        """Сачува подешавања у фајл"""
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def _get_label(self, key):
        lang = self.settings.get('language', DEFAULT_SETTINGS['language'])
        show_icons = self.settings.get('show_icons', True)
        text = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_SETTINGS['language']]).get(key, key)
        if show_icons and key in ICONS:
            return f"{ICONS[key]} {text}"
        return text

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=self._get_label('export_json'), command=self.export_json)
        file_menu.add_command(label=self._get_label('import_json'), command=self.import_json)
        file_menu.add_command(label=self._get_label('export_excel'), command=self.export_excel)
        file_menu.add_command(label=self._get_label('import_excel'), command=self.import_excel)
        file_menu.add_separator()
        file_menu.add_command(label=self._get_label('exit'), command=self.root.destroy)
        menubar.add_cascade(label=self._get_label('file'), menu=file_menu)
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label=self._get_label('all_books'), command=self.prikazi_knjige)
        view_menu.add_command(label=self._get_label('all_authors'), command=self.prikazi_sve_pisce)
        view_menu.add_command(label=self._get_label('statistics'), command=self.otvori_statistiku)
        menubar.add_cascade(label=self._get_label('view'), menu=view_menu)
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label=self._get_label('settings'), command=self.otvori_settings)
        menubar.add_cascade(label=self._get_label('settings'), menu=settings_menu)
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=self._get_label('menu_about_desc'), command=self._show_about_desc)
        help_menu.add_command(label=self._get_label('menu_about_author'), command=self._show_about_author)
        help_menu.add_command(label=self._get_label('menu_about'), command=self._show_about_program)
        menubar.add_cascade(label=self._get_label('menu_help'), menu=help_menu)
        # Back menu
        if hasattr(self, 'current_frame') and self.current_frame is not None and self.current_frame != self.main_frame:
            menubar.add_command(label=self._get_label('back_to_main'), command=self.setup_main_window)
        self.root.config(menu=menubar)

    def _show_about_desc(self):
        messagebox.showinfo(self._get_label('menu_about_desc'), self._get_label('about_desc'))

    def _show_about_author(self):
        messagebox.showinfo(self._get_label('menu_about_author'), self._get_label('about_author'))

    def _show_about_program(self):
        messagebox.showinfo(self._get_label('menu_about'), self._get_label('about_program'))

    def otvori_settings(self):
        dialog = tk.Toplevel(self.root)
        dialog.title(self._get_label('settings'))
        dialog.grab_set()
        # Прикажи иконе
        var_icons = tk.BooleanVar(value=self.settings.get('show_icons', True))
        cb_icons = ttk.Checkbutton(dialog, text=self._get_label('show_icons'), variable=var_icons)
        cb_icons.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        # Избор теме
        tk.Label(dialog, text=self._get_label('theme')).grid(row=1, column=0, padx=10, pady=5, sticky='w')
        var_theme = tk.StringVar(value=self.settings.get('theme', DEFAULT_SETTINGS['theme']))
        combo_theme = ttk.Combobox(dialog, textvariable=var_theme, values=ttk.Style().theme_names(), state='readonly')
        combo_theme.grid(row=1, column=1, padx=10, pady=5)
        # Избор језика
        tk.Label(dialog, text=self._get_label('language')).grid(row=2, column=0, padx=10, pady=5, sticky='w')
        var_lang = tk.StringVar(value=self.settings.get('language', DEFAULT_SETTINGS['language']))
        combo_lang = ttk.Combobox(dialog, textvariable=var_lang, values=list(TRANSLATIONS.keys()), state='readonly')
        combo_lang.grid(row=2, column=1, padx=10, pady=5)
        # Примени
        def apply_and_close():
            self.settings['show_icons'] = var_icons.get()
            self.settings['theme'] = var_theme.get()
            self.settings['language'] = var_lang.get()
            self.save_settings()
            ttk.Style().theme_use(self.settings['theme'])
            self.setup_menu()
            self.setup_main_window()
            dialog.destroy()
        btn_apply = ttk.Button(dialog, text=self._get_label('ok'), command=apply_and_close)
        btn_apply.grid(row=3, column=0, columnspan=2, pady=10)

    def otvori_statistiku(self):
        # Израчунава и приказује статистику библиотеке у табовима
        data = bib.ucitaj_podatke(self.putanja)
        total = ukupno_knjiga(data)
        authors = ukupno_auta(data, bib.podeli_pisce)
        genres = broj_zanrova(data)
        series = broj_serijala(data)
        loans = broj_pozajmica(data)
        knjige_zanr = knjige_po_zanru(data)
        knjige_izdavac = knjige_po_izdavacu(data)
        top5 = top_autori(data, bib.podeli_pisce)
        frame = self.create_new_frame()
        # Креирај посебан фрејм за заглавље
        header_frame = tk.Frame(frame)
        header_frame.grid(row=0, column=0, sticky="ew")
        tk.Label(header_frame, text=self._get_label('statistics'), font=("Helvetica",14,"bold")).grid(row=0, column=0, pady=10, sticky="ew")
        # Таб контрола
        tab_control = ttk.Notebook(frame)
        tab_control.grid(row=1, column=0, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        # --- Опште ---
        tab_opste = tk.Frame(tab_control)
        tab_control.add(tab_opste, text=self._get_label('tab_general'))
        for idx, (label, val) in enumerate([
            (self._get_label('stat_total_books'), total),
            (self._get_label('stat_total_authors'), authors),
            (self._get_label('stat_genres'), genres),
            (self._get_label('stat_series'), series),
            (self._get_label('stat_loans'), loans)
        ]):
            tk.Label(tab_opste, text=f"{label}:", anchor='w').grid(row=idx, column=0, sticky="w", padx=10, pady=5)
            tk.Label(tab_opste, text=str(val), anchor='w').grid(row=idx, column=1, sticky="w", padx=10, pady=5)
        # --- По жанру ---
        tab_zanr = tk.Frame(tab_control)
        tab_control.add(tab_zanr, text=self._get_label('tab_genre'))
        for idx, (zanr, br) in enumerate(sorted(knjige_zanr.items())):
            tk.Label(tab_zanr, text=f"{zanr}:", anchor='w').grid(row=idx, column=0, sticky="w", padx=20, pady=2)
            tk.Label(tab_zanr, text=str(br), anchor='w').grid(row=idx, column=1, sticky="w", pady=2)
        # --- По издавачу ---
        tab_izdavac = tk.Frame(tab_control)
        tab_control.add(tab_izdavac, text=self._get_label('tab_publisher'))
        for idx, (izd, br) in enumerate(sorted(knjige_izdavac.items())):
            tk.Label(tab_izdavac, text=f"{izd}:", anchor='w').grid(row=idx, column=0, sticky="w", padx=20, pady=2)
            tk.Label(tab_izdavac, text=str(br), anchor='w').grid(row=idx, column=1, sticky="w", pady=2)
        # --- Топ 5 аутора ---
        tab_autori = tk.Frame(tab_control)
        tab_control.add(tab_autori, text=self._get_label('tab_top_authors'))
        for idx, (autor, br) in enumerate(top5):
            tk.Label(tab_autori, text=f"{autor}:", anchor='w').grid(row=idx, column=0, sticky="w", padx=20, pady=2)
            tk.Label(tab_autori, text=str(br), anchor='w').grid(row=idx, column=1, sticky="w", pady=2)
        # --- Дијаграм доступности ---
        tab_dijagram = tk.Frame(tab_control)
        tab_control.add(tab_dijagram, text=self._get_label('tab_chart'))
        if Figure:
            labels_chart = [self._get_label('available'), self._get_label('loaned')]
            sizes = [total-loans, loans]
            fig = Figure(figsize=(4,3))
            ax = fig.add_subplot(111)
            ax.pie(sizes, labels=labels_chart, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            canvas = FigureCanvasTkAgg(fig, master=tab_dijagram)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, pady=10)
        else:
            tk.Label(tab_dijagram, text=self._get_label('matplotlib_error'), fg="red").grid(row=0, column=0, pady=10)
        self.show_frame(frame)

    def _compute_availability(self, knjiga):
        """Одређује статус доступности књиге."""
        pos = knjiga.get("Позајмљена", "").strip()
        vra = knjiga.get("Враћена", "").strip()
        if not pos or vra:
            return "Доступна"
        return "Није доступна"

    def _show_loan_details(self, naslov):
        """Приказује детаље о позајмици за књигу."""
        details = bib.pretraga_pozajmica(self.putanja, naslov)
        if details:
            text = "\n".join(f"{k}: {v}" for k, v in details.items())
        else:
            text = "Нема података о позајмици."
        messagebox.showinfo(self._get_label('loan'), text)

    def export_json(self):
        data = bib.ucitaj_podatke(self.putanja)
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files","*.json")])
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                messagebox.showinfo(self._get_label('export_json'), self._get_label('exported_books').format(len(data), path))
            except Exception as e:
                messagebox.showerror(self._get_label('export_json'), f"Грешка: {e}")

    def import_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files","*.json")])
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                    if bib.sacuvaj_podatke(self.putanja, data):
                        messagebox.showinfo(self._get_label('import_json'), self._get_label('imported_books').format(len(data), path))
                        self.go_back()
                    else:
                        messagebox.showerror(self._get_label('import_json'), self._get_label('error_save'))
                else:
                    messagebox.showerror(self._get_label('import_json'), self._get_label('invalid_json'))
            except Exception as e:
                messagebox.showerror(self._get_label('import_json'), f"Грешка: {e}")

    def export_excel(self):
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror(self._get_label('export_excel'), self._get_label('pandas_error'))
            return
        data = bib.ucitaj_podatke(self.putanja)
        df = pd.DataFrame(data)
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if path:
            try:
                df.to_excel(path, index=False)
                messagebox.showinfo(self._get_label('export_excel'), self._get_label('exported_books').format(len(data), path))
            except Exception as e:
                messagebox.showerror(self._get_label('export_excel'), f"Грешка: {e}")
    
    # Отвара форму за додавање нове књиге 
    def otvori_dodavanje(self):
        frame = self.create_new_frame()
        fields = ["Наслов", "Писац", "Година издавања", "Жанр", "Серијал",
              "Колекција", "Издавач", "ИСБН", "Повез", "Напомена"]
        entries = {}
        entries_authors = []
        
        for i, field in enumerate(fields):
            tk.Label(frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5)
            if field == "Писац":
                # Креирамо посебну секцију за ауторе
                author_section = tk.LabelFrame(frame, text=self._get_label('authors'), padx=2, pady=2)
                author_section.grid(row=i, column=1, padx=5, pady=5, sticky="nsew")
                frame.grid_rowconfigure(i, weight=1)
                frame.grid_columnconfigure(1, weight=1)
                author_section.grid_rowconfigure(0, weight=1)
                author_section.grid_columnconfigure(0, weight=1)

                # Use grid for the scrollable frame
                scrollable_authors = ScrollableFrame(author_section, height=120)
                scrollable_authors.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
                authors_container = scrollable_authors.get_frame()
                authors_container.grid_columnconfigure(1, weight=1)
                entries_authors = []

                def add_author_field(name=""):
                    row = len(entries_authors)
                    btn_remove = ttk.Button(authors_container, text="-", width=2, command=lambda r=row: remove_author_field(r))
                    btn_remove.grid(row=row, column=0, padx=2, pady=2, sticky="nw")
                    entry = ttk.Combobox(authors_container, values=pisci, width=25)
                    entry.grid(row=row, column=1, padx=2, pady=2, sticky="ew")
                    entry.insert(0, name)
                    authors_container.grid_rowconfigure(row, weight=0)
                    entries_authors.append(entry)

                def remove_author_field(row):
                    if 0 <= row < len(entries_authors):
                        entries_authors[row].destroy()
                        entries_authors.pop(row)
                        for i, entry in enumerate(entries_authors):
                            btn = None
                            for widget in authors_container.grid_slaves(row=i, column=0):
                                if isinstance(widget, ttk.Button):
                                    btn = widget
                                    break
                            if btn:
                                btn.grid(row=i, column=0, padx=2, pady=2, sticky="nw")
                            entry.grid(row=i, column=1, padx=2, pady=2, sticky="ew")
                    else:
                        print(f"[DEBUG] Покушај брисања невалидног аутора: {row}")

                # Додај поље за првог аутора
                add_author_field()

                # Додај контроле за додавање новог аутора
                add_author_frame = tk.Frame(author_section)
                add_author_frame.grid(row=1, column=0, sticky="ew", pady=(5,0))
                add_author_frame.grid_columnconfigure(0, weight=1)
                new_author_entry = ttk.Combobox(add_author_frame, values=pisci, width=25)
                new_author_entry.grid(row=0, column=0, padx=2, sticky="ew")
                add_author_frame.grid_columnconfigure(0, weight=1)

                def add_new_author_from_entry():
                    name = new_author_entry.get().strip()
                    if name:
                        add_author_field(name)
                        new_author_entry.delete(0, tk.END)

                btn_add = ttk.Button(add_author_frame, text="+", width=2, command=add_new_author_from_entry)
                btn_add.grid(row=0, column=1, padx=2)
                entries["Писац"] = entries_authors
                
            elif field == "Жанр":
                entry = ttk.Combobox(frame, values=zanr, width=25)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                entries[field] = entry
            elif field == "Издавач":
                entry = ttk.Combobox(frame, values=izdavac, width=25)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                entries[field] = entry
            elif field == "Повез":
                entry = ttk.Combobox(frame, values=povez, width=25)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                entries[field] = entry
            else:
                entry = tk.Entry(frame)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                entries[field] = entry
        # Додаје дугме за чување нове књиге
        def sacuvaj():
            global zanr, izdavac, pisci
            # Construct new book data including dynamic authors
            nova_knjiga = {}
            for field in fields:
                if field == "Писац":
                    # Прикупи све ауторе из појединачних поља и споји их са тачка-запетом
                    authors = [e.get() for e in entries_authors if e.get().strip()]
                    nova_knjiga[field] = "; ".join(authors)
                elif field in ["Жанр", "Издавач", "Повез"]:
                    widget = entries[field]
                    value = widget.get() if hasattr(widget, 'get') else widget
                    nova_knjiga[field] = value
                else:
                    widget = entries[field]
                    value = widget.get() if hasattr(widget, 'get') else widget
                    if field in ["Наслов", "Година издавања"] and not value:
                        messagebox.showerror(self._get_label('error'), f"Поље '{field}' је обавезно!")
                        return
                    if field == "Година издавања" and value and not value.isdigit():
                        messagebox.showerror(self._get_label('error'), "Година мора бити број!")
                        return
                    nova_knjiga[field] = value
            
            # Провера обавезних поља
            for obavezno_polje in ["Наслов", "Писац"]:
                if not nova_knjiga.get(obavezno_polje):
                    messagebox.showerror(self._get_label('error'), f"Поље '{obavezno_polje}' је обавезно!")
                    return
                
            if bib.dodaj_knjigu(self.putanja, nova_knjiga):
                # Ажурирамо глобалне листе након додавања
                global zanr, izdavac, pisci
                # Ажурирамо регистар писаца и друге податке
                if hasattr(bib, 'inicijalizuj_podatke'):
                    azurirani_podaci = bib.inicijalizuj_podatke(self.putanja)
                    zanr = azurirani_podaci['zanr']
                    izdavac = azurirani_podaci['izdavac']
                    pisci = azurirani_podaci['pisci']
                messagebox.showinfo(self._get_label('success'), self._get_label('book_added'))
                self.go_back()
            else:
                messagebox.showerror(self._get_label('error'), self._get_label('error_adding_book'))
        
        # Save button always at the bottom
        btn_save = tk.Button(frame, text=self._get_label('save'), command=sacuvaj)
        btn_save.grid(row=len(fields), column=0, columnspan=3, pady=10, sticky="ew")
        self.show_frame(frame)
    
    # Отвара форму за претрагу позајмљених књига
    def otvori_pozajmice(self):
        frame = self.create_new_frame()
        tk.Label(frame, text=self._get_label('enter_book_title')).grid(row=0, column=0, pady=5)
        unos = tk.Entry(frame)
        unos.grid(row=1, column=0, pady=5)
        def pretrazi_pozajmicu():
            # Претражује позајмицу.
            rezultat = bib.pretraga_pozajmica(self.putanja, unos.get())
            if rezultat:
                tekst = "\n".join([f"{k}: {v}" for k, v in rezultat.items()])
                messagebox.showinfo(self._get_label('loan'), tekst)
            else:
                messagebox.showinfo(self._get_label('information'), self._get_label('book_not_found'))
        tk.Button(frame, text=self._get_label('search'), command=pretrazi_pozajmicu).grid(row=2, column=0, pady=5)
        self.show_frame(frame)
    
    # Отвара форму за претрагу књига
        self.show_frame(frame)
    
    # Отвара форму за брисање књиге
    def otvori_brisanje(self):
        frame = self.create_new_frame()
        tk.Label(frame, text=self._get_label('enter_book_title_delete')).grid(row=0, column=0, pady=5)
        unos = tk.Entry(frame)
        unos.grid(row=1, column=0, pady=5)
        def obrisi():
            # Брише књигу са датим насловом.
            naslov = unos.get()
            if naslov:
                odgovor = messagebox.askyesno("Потврда", f"Да ли сте сигурни да желите да обришете књигу '{naslov}'?")
                if odgovor and bib.obrisi_knjigu(self.putanja, naslov):
                    messagebox.showinfo("Успех", "Књига је успешно обрисана.")
                    self.go_back()
                else:
                    messagebox.showerror("Грешка", "Књига није пронађена или је дошло до грешке при брисању.")
        tk.Button(frame, text=self._get_label('delete'), command=obrisi).grid(row=2, column=0, pady=5)
        self.show_frame(frame)
    
    def import_excel(self):
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror(self._get_label('import_excel'), self._get_label('pandas_error'))
            return
        path = filedialog.askopenfilename(filetypes=[("Excel files","*.xlsx")])
        if path:
            try:
                df = pd.read_excel(path)
                data = df.to_dict(orient='records')
                if bib.sacuvaj_podatke(self.putanja, data):
                    messagebox.showinfo(self._get_label('import_excel'), self._get_label('imported_books').format(len(data), path))
                    self.go_back()
                else:
                    messagebox.showerror(self._get_label('import_excel'), self._get_label('error_save'))
            except Exception as e:
                messagebox.showerror(self._get_label('import_excel'), f"Грешка: {e}")

# ToolTip helper for widgets
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
    def show(self, event=None):
        if self.tipwindow or not self.text:
            return
        x = event.x_root + 10
        y = event.y_root + 10
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0", relief="solid", borderwidth=1, font=("tahoma","8","normal"))
        label.pack(ipadx=1)
    def hide(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def main(putanja_do_bcsv):
    # Обезбеђујемо да су сви потребни подаци учитани
    global zanr, izdavac, povez, pisci
    
    # Иницијализујемо податке из CSV фајла
    if hasattr(bib, 'inicijalizuj_podatke'):
        podaci = bib.inicijalizuj_podatke(putanja_do_bcsv)
        zanr = podaci['zanr']
        izdavac = podaci['izdavac']
        povez = podaci['povez']
        pisci = podaci['pisci']
    
    # Покрени главни прозор
    root = tk.Tk()
    app = BibliotekaGUI(root, putanja_do_bcsv)
    root.mainloop()