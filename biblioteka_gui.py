# -*- coding: utf-8 -*-
# @Аутор    : minciv
# @Фајл     : biblioteka_gui.py
# @Верзија  : 0.2.0
# @Програм  : Windsurf
# @Опис     : Графички интерфејс за програм Кућна Библиотека

# Увозимо потребне модуле
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import Biblioteka as bib
from scrollable_frame import ScrollableFrame
import os
import json
from translations import TRANSLATIONS, ICONS
from help_texts import HELP_TEXTS, ABOUT_TEXTS

# Додајемо Pillow за рад са сликама
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    ImageTk = None
    PIL_AVAILABLE = False
    
# Увозимо менаџер икона
try:
    from icon_manager import initialize_icons, get_icon_manager
    # Иницијализујемо менаџер икона
    icon_manager = initialize_icons()
    ICON_SUPPORT = True
except ImportError:
    ICON_SUPPORT = False
    
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
    'show_icons': True,
    'use_png_icons': True
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
    ukupno_knjiga, ukupno_autora, broj_zanrova, broj_serijala, broj_pozajmica,
    knjige_po_zanru, knjige_po_izdavacu, top_autori
)

# Ствара класу Библиотека
class BibliotekaGUI:
    def __init__(self, root, putanja):
        self.root = root
        self.putanja = putanja  # Сачувај путању као атрибут
        self.frame_stack = []  # Иницијализација стека фрејмова
        self.root.title("Кућна Библиотека")
        # Постављање иконице апликације ако постоји
        try:
            if Image and ImageTk:
                ikona_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ikona_kucna_biblioteka_64.png')
                if os.path.exists(ikona_path):
                    ikona_img = Image.open(ikona_path)
                    self._icon_img = ImageTk.PhotoImage(ikona_img)
                    self.root.iconphoto(True, self._icon_img)
        except Exception as e:
            pass  # Ако нешто не ради, настави без иконице
        self.current_frame = None
        self.history = []  # Stack for navigation history
        self.language = "sr_CYRL"  # Default language
        self.status_bar = None
        self.progress_var = tk.DoubleVar()
        
        # Постављање наслова и иконе
        self.root.title("Кућна библиотека")
        try:
            self.root.iconphoto(True, tk.PhotoImage(file="ikona_kucna_biblioteka.png"))
        except Exception as e:
            print(f"Грешка при учитавању иконе: {e}")
        
        # Главни контејнер
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        
        # Додај статусну траку
        self.create_status_bar()
        
        # Учитавање PNG икона
        if PIL_AVAILABLE:
            try:
                icon_manager = get_icon_manager()
                icon_manager.load_icons(self.root)
                self.update_status("PNG иконе су успешно учитане")
            except Exception as e:
                self.update_status(f"Грешка при учитавању PNG икона: {e}", error=True)
        
        # Учитај подешавања
        self.load_settings()
        
        # Учитај податке у посебној нити
        self.load_data_async(self.putanja)
        
        self.setup_menu()
        self.setup_main_window()
        self.root.minsize(800, 600)
        # Keyboard shortcuts
        self.root.bind_all("<Control-n>", lambda e: self.otvori_dodavanje())
        self.root.bind_all("<Control-s>", lambda e: self.save_current_form())  # Save shortcut
        self.root.bind_all("<Control-f>", lambda e: self.otvori_pretragu())
        self.root.bind_all("<Escape>", lambda e: self.go_back())

    # Функција за креирање статусне траке
    def create_status_bar(self):
        """Креира статусну траку на дну прозора"""
        status_frame = tk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = tk.Label(status_frame, text="Спремно", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Додај прогрес бар
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        self.progress_bar.pack_forget()  # Сакриј док није потребан
    
    # Функција за поновно учитавање података
    def update_status(self, message, error=False):
        """Ажурира статусну траку са поруком"""
        if self.status_bar:
            self.status_bar.config(text=message, fg="red" if error else "black")
            self.root.update_idletasks()
    
    # Функција за приказује или сакрива прогрес бар
    def show_progress(self, show=True):
        """Приказује или сакрива прогрес бар"""
        if show:
            self.progress_bar.pack(side=tk.RIGHT, padx=5)
        else:
            self.progress_bar.pack_forget()
        self.root.update_idletasks()
    
    # Функција за асинхроно учитавање података
    def load_data_async(self, data_path):
        """Учитава податке асинхроно у посебној нити"""
        import threading
        
        def load_task():
            self.update_status("Учитавање података...")
            self.show_progress(True)
            self.progress_var.set(10)
            self.root.update_idletasks()
            
            try:
                # Симулирај прогрес
                import time
                for i in range(10, 100, 10):
                    time.sleep(0.1)  # Симулација дужег учитавања
                    self.progress_var.set(i)
                    self.root.update_idletasks()
                
                # Учитај податке
                self.data = bib.ucitaj_podatke(data_path)
                self.progress_var.set(100)
                
                # Ажурирај UI у главној нити
                self.root.after(0, lambda: self.update_status(f"Учитано {len(self.data)} књига"))
                self.root.after(100, lambda: self.show_progress(False))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Грешка при учитавању: {e}", error=True))
                self.root.after(100, lambda: self.show_progress(False))
        
        # Покрени нит
        thread = threading.Thread(target=load_task)
        thread.daemon = True
        thread.start()

    # Функција за памћење података
    def save_current_form(self):
        # Плацехолдер: имплементирајте ако желите да Ctrl+S изазове снимање у текућем облику
        pass
    
    # Функција за отварање прозора за претрагу
    def otvori_pretragu(self):
        self.root.bind_all("<Control-f>", lambda e: self.otvori_pretragu())
        self.root.bind_all("<Escape>", lambda e: self.go_back())

    # Поставља главни прозор са дугметима за различите акције.
    def setup_main_window(self):
        """Поставља главни прозор са дугмадима и модерним UI елементима."""
        self.main_frame = tk.Frame(self.container)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Стилизовани наслов са модерним изгледом
        header_frame = tk.Frame(self.main_frame, bg="#3a7ebf")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = tk.Label(header_frame, text="Кућна библиотека", 
                              font=("Helvetica", 18, "bold"), 
                              fg="white", bg="#3a7ebf", 
                              padx=10, pady=10)
        title_label.grid(row=0, column=0)
        
        # Главни садржај у оквиру
        content_frame = ttk.LabelFrame(self.main_frame, text=self._get_label('main_menu'))
        content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Команде за дугмад
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
        
        # Додаје дугме за статистику
        commands.append(("statistics", self.otvori_statistiku))
        
        # Пречице са тастатуре 
        shortcuts = {self.otvori_dodavanje: "Ctrl+N", self.otvori_pretragu: "Ctrl+F", self.go_back: "Esc"}
        
        # Креирамо модерни стил за дугмад
        button_style = ttk.Style()
        button_style.configure("Modern.TButton", font=("Helvetica", 11), padding=8)
        
        # Креирамо дугмад са иконама у модерном стилу
        for i, (key, command) in enumerate(commands):
            # Креирамо оквир за дугме и опис
            btn_frame = tk.Frame(content_frame)
            btn_frame.grid(row=i, column=0, pady=5, padx=10, sticky="ew")
            btn_frame.grid_columnconfigure(1, weight=1)
            
            # Креирамо дугме са иконом
            btn = self._create_button_with_icon(btn_frame, key, command, style="Modern.TButton")
            btn.grid(row=0, column=0, padx=(0, 10))
            
            # Додајемо опис функције дугмета
            text_only = TRANSLATIONS.get(self.settings.get('language', DEFAULT_SETTINGS['language']), 
                                      TRANSLATIONS[DEFAULT_SETTINGS['language']]).get(key, key)
            desc_label = tk.Label(btn_frame, text=text_only, anchor="w", justify="left")
            desc_label.grid(row=0, column=1, sticky="w")
            
            # Додајемо tooltip са пречицом ако постоји
            sc = shortcuts.get(command)
            if sc:
                ToolTip(btn, f"{text_only} ({sc})")
        
        # Додајемо информацију о верзији на дну
        version_frame = tk.Frame(self.main_frame)
        version_frame.grid(row=2, column=0, pady=(10, 5), sticky="ew")
        version_label = tk.Label(version_frame, text="v0.2.0", fg="gray")
        version_label.pack(side="right", padx=10)
        
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
        def pretrazi_izabranogpisca():
            selection = pisci_listbox.curselection()
            if selection:
                pisac = pisci_listbox.get(selection[0])
                self.pretrazi_po_piscu(pisac)
            else:
                messagebox.showinfo("Обавештење", "Најпре изаберите писца из листе.")
        
        btn = ttk.Button(frame, text=self._get_label('search_author_books'), command=pretrazi_izabranogpisca)
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
        # Проверава да ли дугме "Назад" већ постоји
        back_button_exists = False
        for child in frame.grid_slaves():
            if isinstance(child, (tk.Button, ttk.Button)) and child.cget("text") in [self._get_label('back')]:
                back_button_exists = True
                break
        
        # Ако дугме "Назад" не постоји, додаје ново
        if not back_button_exists:
            # Проверавамо да ли постоји посебан фрејм за дугме "Назад"
            back_frame = None
            for child in frame.grid_slaves():
                if isinstance(child, tk.Frame) and child.grid_info()['row'] == 2:
                    back_frame = child
                    break
            
            # Ако постоји посебан фрејм за дугме "Назад" (као у статистици), користимо њега
            if back_frame:
                btn = self._create_button_with_icon(back_frame, 'back', self.go_back)
                btn.pack(side=tk.LEFT, padx=10)
            else:
                # Проналази последњи ред у фрејму
                last_row = 0
                for child in frame.grid_slaves():
                    last_row = max(last_row, child.grid_info()['row'])
                # Креирамо дугме са иконом
                btn = self._create_button_with_icon(frame, 'back', self.go_back)
                btn.grid(row=last_row + 1, column=0, columnspan=2, pady=10, sticky="ew")

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
    def create_treeview_with_scrollbar(self, frame, columns, column_widths, tag_config=True):
        """Креира модеран табеларни приказ са клизачем и напредним стиловима"""
        # Креирамо оквир за табелу
        table_frame = ttk.LabelFrame(frame, text=self._get_label('books_list'))
        table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Креирамо модерне стилове за табелу
        style = ttk.Style()
        style.configure("Treeview", 
                      rowheight=30,  # Већа висина редова
                      font=("Helvetica", 10),
                      background="#f0f0f0",
                      fieldbackground="#f0f0f0")
        
        # Стил за заглавља колона
        style.configure("Treeview.Heading", 
                      font=("Helvetica", 10, "bold"),
                      background="#e0e0e0")
        
        # Креирамо табелу
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Подешавамо колоне
        for col, width in zip(columns, column_widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, minwidth=50)
        
        # Додајемо клизаче
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Постављамо компоненте
        tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        # Конфигуришемо тагове за различите статусе књига
        if tag_config:
            tree.tag_configure('dostupna', background='#e6ffe6')  # Светло зелена за доступне књиге
            tree.tag_configure('pozajmljena', background='#ffe6e6')  # Светло црвена за позајмљене
            tree.tag_configure('rezervisana', background='#fff2e6')  # Наранџаста за резервисане
        
        # Подешавамо да фрејм и табела попуне простор
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        return tree

    # Изменена функција prikazi_rezultate да користи помоћну функцију
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

    # Модеернизована функција prikazi_knjige са напредним UI елементима
    def prikazi_knjige(self):
        """Приказује све књиге у модерном табеларном приказу са напредним функцијама"""
        # Приказујемо индикатор учитавања
        self.update_status(self._get_label('loading_data'))
        self.show_progress(True)
        self.progress_var.set(10)
        self.root.update_idletasks()
        
        # Учитавамо податке
        podaci = bib.ucitaj_podatke(self.putanja)
        self.progress_var.set(50)
        self.root.update_idletasks()
        
        if not podaci:
            self.show_progress(False)
            messagebox.showinfo(self._get_label('information'), self._get_label('no_books_found'))
            return
        
        # Креирамо главни фрејм
        frame = self.create_new_frame()
        frame.grid_rowconfigure(1, weight=1)  # Табела заузима већину простора
        frame.grid_rowconfigure(2, weight=0)  # Доњи део за филтере и дугмад
        frame.grid_columnconfigure(0, weight=1)
        
        # Додајемо наслов
        header_frame = tk.Frame(frame, bg="#3a7ebf")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = tk.Label(header_frame, text=self._get_label('all_books'), 
                              font=("Helvetica", 14, "bold"), 
                              fg="white", bg="#3a7ebf", 
                              padx=10, pady=5)
        title_label.grid(row=0, column=0, sticky="w")
        
        # Додајемо информацију о броју књига
        count_label = tk.Label(header_frame, text=f"{len(podaci)} {self._get_label('books_found')}", 
                              font=("Helvetica", 10), 
                              fg="white", bg="#3a7ebf", 
                              padx=10, pady=5)
        count_label.grid(row=0, column=1, sticky="e")
        
        # Дефинишемо колоне и ширине
        columns = ("Наслов", "Писац", "Година издавања", "Доступност")
        column_widths = (250, 180, 120, 120)
        
        # Креирамо табеларни приказ са модерним стиловима
        tree = self.create_treeview_with_scrollbar(frame, columns, column_widths)
        # Постављамо табелу у ред 1, испод наслова
        tree.master.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Додајемо податке у табелу са одговарајућим таговима за боје
        for knjiga in podaci:
            dostup = self._compute_availability(knjiga)
            tag = 'dostupna' if dostup == "Доступна" else 'pozajmljena'
            tree.insert("", "end", values=(
                knjiga.get("Наслов",""), 
                knjiga.get("Писац",""), 
                knjiga.get("Година издавања",""), 
                dostup
            ), tags=(tag,))
        
        # Додајемо панел са филтерима и дугмадима
        control_frame = ttk.LabelFrame(frame, text=self._get_label('options'))
        control_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=1)
        
        # Додајемо поље за брзу претрагу
        search_frame = tk.Frame(control_frame)
        search_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        tk.Label(search_frame, text=self._get_label('quick_search')).pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Функција за филтрирање по претрази
        def filter_by_search(*args):
            search_text = search_var.get().lower()
            for item in tree.get_children():
                values = tree.item(item, 'values')
                if search_text in values[0].lower() or search_text in values[1].lower():
                    tree.item(item, tags=tree.item(item, 'tags'))
                else:
                    tree.detach(item)  # Сакриј ставку
            
            # Ако је поље празно, прикажи све књиге
            if not search_text:
                tree.delete(*tree.get_children())
                for knjiga in podaci:
                    dostup = self._compute_availability(knjiga)
                    tag = 'dostupna' if dostup == "Доступна" else 'pozajmljena'
                    tree.insert("", "end", values=(
                        knjiga.get("Наслов",""), 
                        knjiga.get("Писац",""), 
                        knjiga.get("Година издавања",""), 
                        dostup
                    ), tags=(tag,))
        
        # Повезујемо функцију са променом текста у пољу за претрагу
        search_var.trace("w", filter_by_search)
        
        # Додајемо филтер за доступност
        filter_frame = tk.Frame(control_frame)
        filter_frame.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(filter_frame, text=self._get_label('filter_by')).pack(side=tk.LEFT, padx=5)
        filter_var = tk.StringVar(value="all")
        filter_combo = ttk.Combobox(filter_frame, textvariable=filter_var, 
                                  values=["all", "dostupna", "pozajmljena"], 
                                  width=15, state="readonly")
        filter_combo.pack(side=tk.LEFT, padx=5)
        
        # Функција за филтрирање по доступности
        def filter_by_availability(*args):
            filter_value = filter_var.get()
            if filter_value == "all":
                filter_by_search()  # Примени само текстуалну претрагу
                return
                
            # Примени филтер доступности
            tree.delete(*tree.get_children())
            for knjiga in podaci:
                dostup = self._compute_availability(knjiga)
                tag = 'dostupna' if dostup == "Доступна" else 'pozajmljena'
                
                # Провери да ли књига задовољава филтер
                if (filter_value == "dostupna" and dostup == "Доступна") or \
                   (filter_value == "pozajmljena" and dostup != "Доступна"):
                    # Провери и текстуалну претрагу
                    search_text = search_var.get().lower()
                    if not search_text or search_text in knjiga.get("Наслов","").lower() or \
                       search_text in knjiga.get("Писац","").lower():
                        tree.insert("", "end", values=(
                            knjiga.get("Наслов",""), 
                            knjiga.get("Писац",""), 
                            knjiga.get("Година издавања",""), 
                            dostup
                        ), tags=(tag,))
        
        # Повезујемо функцију са променом вредности у комбо боксу
        filter_var.trace("w", filter_by_availability)
        
        # Додајемо дугмад за акције
        button_frame = tk.Frame(control_frame)
        button_frame.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        # Дугме за детаље
        def show_selected_details():
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
        
        details_btn = ttk.Button(button_frame, text=self._get_label('details'), 
                               command=show_selected_details, style="Modern.TButton")
        details_btn.pack(side=tk.LEFT, padx=5)
        
        # Функције за догађаје
        def on_double(event):
            show_selected_details()
        
        def on_right_click(event):
            # Прво селектујемо ставку на којој је кликнуто
            item = tree.identify_row(event.y)
            if item:
                # Селектујемо ставку
                tree.selection_set(item)
                # Приказујемо контекстни мени
                self._show_context_menu(event, tree, podaci)
        
        # Повезујемо догађаје
        tree.bind("<Double-1>", on_double)
        tree.bind("<Button-3>", on_right_click)  # Button-3 је десни клик
        
        # Сакривамо прогрес бар и приказујемо фрејм
        self.progress_var.set(100)
        self.update_status(self._get_label('data_loaded'))
        self.root.after(500, lambda: self.show_progress(False))
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
                        fields = ["Наслов", "Писац", "Година издавања", "Жанр", "Серијал", "Колекција", "Издавачи", "ИСБН", "Повез", "Напомена", "Позајмљена", "Враћена", "Ко је позајмио"]
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
                            elif field == "Издавачи":
                                publisher_section = tk.LabelFrame(edit_frame, text=self._get_label('publishers'), padx=2, pady=2)
                                publisher_section.grid(row=i+1, column=1, padx=5, pady=5, sticky="nsew", columnspan=2)
                                edit_frame.grid_rowconfigure(i+1, weight=1)
                                edit_frame.grid_columnconfigure(1, weight=1)
                                publisher_section.grid_rowconfigure(0, weight=1)
                                publisher_section.grid_columnconfigure(0, weight=1)

                                scrollable_publishers = ScrollableFrame(publisher_section, height=120)
                                scrollable_publishers.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
                                publishers_container = scrollable_publishers.get_frame()
                                # Правилна конфигурација за приказ издавача један испод другог
                                publishers_container.grid_columnconfigure(1, weight=1)
                                # Поставља правилну конфигурацију за вертикални приказ
                                for i in range(10):
                                    publishers_container.grid_rowconfigure(i, weight=0)
                                entries_publishers = []

                                def add_publisher_field_edit(name=""):
                                    row = len(entries_publishers)
                                    btn_remove = ttk.Button(publishers_container, text="-", width=2, command=lambda r=row: remove_publisher_field(r))
                                    btn_remove.grid(row=row, column=0, padx=2, pady=2, sticky="nw")
                                    entry = ttk.Combobox(publishers_container, values=izdavac, width=25)
                                    entry.grid(row=row, column=1, padx=2, pady=2, sticky="ew")
                                    entry.insert(0, name)
                                    publishers_container.grid_rowconfigure(row, weight=0)
                                    entries_publishers.append(entry)

                                def remove_publisher_field(row):
                                    if 0 <= row < len(entries_publishers):
                                        entries_publishers[row].destroy()
                                        entries_publishers.pop(row)
                                        for i, entry in enumerate(entries_publishers):
                                            btn = None
                                            for widget in publishers_container.grid_slaves(row=i, column=0):
                                                if isinstance(widget, ttk.Button):
                                                    btn = widget
                                                    break
                                            if btn:
                                                btn.grid(row=i, column=0, padx=2, pady=2, sticky="nw")
                                            entry.grid(row=i, column=1, padx=2, pady=2, sticky="ew")
                                    else:
                                        print(f"[DEBUG] Покушај брисања невалидног издавача: {row}")

                                # Узимамо издаваче директно из објекта књиге
                                existing_publishers = []
                                if "Издавачи" in knjiga and knjiga["Издавачи"]:
                                    existing_publishers = knjiga["Издавачи"].split("; ")
                                # Ако књига има старо поље "Издавач", користимо то
                                elif "Издавач" in knjiga and knjiga["Издавач"]:
                                    # Раздвајамо издаваче по тачка-зарезу, баш као што се ради и за поље "Издавачи"
                                    existing_publishers = knjiga["Издавач"].split("; ")
                                    
                                for name in existing_publishers:
                                    add_publisher_field_edit(name)
                                if not existing_publishers:
                                    add_publisher_field_edit()

                                add_publisher_frame = tk.Frame(publisher_section)
                                add_publisher_frame.grid(row=1, column=0, sticky="ew", pady=(5,0))
                                add_publisher_frame.grid_columnconfigure(0, weight=1)
                                new_publisher_entry = ttk.Combobox(add_publisher_frame, values=izdavac, width=25)
                                new_publisher_entry.grid(row=0, column=0, padx=2, sticky="ew")

                                def add_new_publisher_from_entry():
                                    name = new_publisher_entry.get().strip()
                                    if name:
                                        add_publisher_field_edit(name)
                                        new_publisher_entry.delete(0, tk.END)

                                btn_add = ttk.Button(add_publisher_frame, text="+", width=2, command=add_new_publisher_from_entry)
                                btn_add.grid(row=0, column=1, padx=2)
                                entries[field] = entries_publishers
                            elif field == "Жанр":
                                entry = ttk.Combobox(edit_frame, values=zanr, width=25)
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
                                    authors = [e.get() for e in entries_authors if e.get().strip()]
                                    nova_knjiga[field] = "; ".join(authors)
                                elif field == "Издавачи":
                                    publishers = [e.get() for e in entries_publishers if e.get().strip()]
                                    # Чувамо у поље "Издавач" за компатибилност са CSV
                                    nova_knjiga["Издавач"] = "; ".join(publishers)
                                elif field in ["Жанр"]:
                                    val = entries[field].get() if hasattr(entries[field], 'get') else str(entries[field])
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
                odgovor = messagebox.askyesno("Потврда", f"Да ли сте сигурни да желите да обришете књигу '{naslov}'?")
                if odgovor and bib.obrisi_knjigu(self.putanja, naslov):  # Fixed: replaced Cyrillic 'и' with 'and'
                    messagebox.showinfo("Успех", "Књига је успешно обрисана.")
                    self.go_back()
                else:
                    messagebox.showerror("Грешка", "Књига није пронађена или је дошло до грешке при брисању.")
        # Креирамо дугме за брисање са иконом
        delete_btn = self._create_button_with_icon(frame, 'delete_book', obrisi)
        delete_btn.grid(row=2, column=0, pady=5)
        self.show_frame(frame)
    
    # Отвара форму за претрагу књига
    def otvori_pretragu(self):
        frame = self.create_new_frame()
        tk.Label(frame, text=self._get_label('search_options')).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Освежавамо листе писаца, жанрова и издавача
        global zanr, izdavac, pisci
        try:
            podaci = bib.inicijalизуј_podatке(self.putanja)
            zanr = podaci['zanr']
            izdavac = podaci['izdavac']
            pisci = podaci['pisci']
        except Exception as e:
            print(f"[DEBUG] Грешка при учитавању података: {e}")
        
        # Креира поља за претрагу - искључујемо Повез из критеријума
        fields = ["Наслов", "Писац", "Година издавања", "Жанр", "Издавачи"]
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
                entry = ttk.Combobox(frame, values=poveз, width=25)
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
        
        # Креирамо дугме за претрагу са иконом
        search_btn = self._create_button_with_icon(frame, 'search_books', pretrazi)
        search_btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)
        self.show_frame(frame)
    
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
        """Креира нови фрејм за приказ садржаја"""
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
        use_png_icons = self.settings.get('use_png_icons', True) and ICON_SUPPORT and PIL_AVAILABLE
        
        text = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_SETTINGS['language']]).get(key, key)
        
        # Ако користимо PNG иконе, враћамо само текст који ће се приказати поред иконе
        if use_png_icons:
            return text
        # Ако користимо емоџије као иконе
        elif show_icons and key in ICONS:
            return f"{ICONS[key]} {text}"
        return text
    
    def _create_button_with_icon(self, parent, key, command, style=None, **kwargs):
        """Креира дугме са иконом ако је доступна, са опционим стилом"""
        use_png_icons = self.settings.get('use_png_icons', True) and ICON_SUPPORT and PIL_AVAILABLE
        show_icons = self.settings.get('show_icons', True)
        
        text = self._get_label(key)
        
        # Додајемо стил ако је прослеђен
        if style:
            kwargs['style'] = style
        
        # Ако користимо PNG иконе и подржане су
        if use_png_icons and show_icons:
            icon_manager = get_icon_manager()
            icon = icon_manager.get_icon(key)
            if icon:
                btn = ttk.Button(parent, text=text, image=icon, compound=tk.LEFT, command=command, **kwargs)
                return btn
        
        # Ако користимо Unicode иконе или PNG нису доступне
        if show_icons and key in ICONS:
            btn = ttk.Button(parent, text=f"{ICONS[key]} {text}", command=command, **kwargs)
        else:
            btn = ttk.Button(parent, text=text, command=command, **kwargs)
            
        return btn

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        
        # Проверавамо да ли користимо PNG иконе
        use_png_icons = self.settings.get('use_png_icons', True) and ICON_SUPPORT and PIL_AVAILABLE
        
        # Функција за додавање ставке у мени са иконом
        def add_menu_item_with_icon(menu, key, command):
            if use_png_icons:
                # Добављамо икону
                icon = get_icon_manager().get_icon(key, self.root)
                if icon:
                    menu.add_command(label=self._get_label(key), command=command, image=icon, compound=tk.LEFT)
                    # Чувамо референцу на икону
                    if not hasattr(menu, 'icons'):
                        menu.icons = {}
                    menu.icons[key] = icon
                else:
                    menu.add_command(label=self._get_label(key), command=command)
            else:
                menu.add_command(label=self._get_label(key), command=command)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        add_menu_item_with_icon(file_menu, 'export_json', self.export_json)
        add_menu_item_with_icon(file_menu, 'import_json', self.import_json)
        add_menu_item_with_icon(file_menu, 'export_excel', self.export_excel)
        add_menu_item_with_icon(file_menu, 'import_excel', self.import_excel)
        file_menu.add_separator()
        add_menu_item_with_icon(file_menu, 'exit', self.root.destroy)
        menubar.add_cascade(label=self._get_label('file'), menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        add_menu_item_with_icon(view_menu, 'all_books', self.prikazi_knjige)
        add_menu_item_with_icon(view_menu, 'all_authors', self.prikazi_sve_pisce)
        add_menu_item_with_icon(view_menu, 'statistics', self.otvori_statistiku)
        menubar.add_cascade(label=self._get_label('view'), menu=view_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        add_menu_item_with_icon(settings_menu, 'settings', self.otvori_settings)
        menubar.add_cascade(label=self._get_label('settings'), menu=settings_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=self._get_label('menu_help'), command=self.show_help_window)
        help_menu.add_separator()
        help_menu.add_command(label=self._get_label('menu_license'), command=self.show_license)
        help_menu.add_separator()
        help_menu.add_command(label=self._get_label('menu_about_desc'), command=self._show_about_desc)
        help_menu.add_command(label=self._get_label('menu_about_author'), command=self._show_about_author)
        help_menu.add_command(label=self._get_label('menu_about'), command=self._show_about_program)
        menubar.add_cascade(label=self._get_label('menu_help'), menu=help_menu)
        
        # Back menu
        if hasattr(self, 'current_frame') and self.current_frame is not None and self.current_frame != self.main_frame:
            if use_png_icons:
                icon = get_icon_manager().get_icon('back_to_main', self.root)
                if icon:
                    menubar.add_command(label=self._get_label('back_to_main'), command=self.setup_main_window, 
                                       image=icon, compound=tk.LEFT)
                    # Чувамо референцу на икону
                    if not hasattr(menubar, 'icons'):
                        menubar.icons = {}
                    menubar.icons['back_to_main'] = icon
                else:
                    menubar.add_command(label=self._get_label('back_to_main'), command=self.setup_main_window)
            else:
                menubar.add_command(label=self._get_label('back_to_main'), command=self.setup_main_window)
        
        self.root.config(menu=menubar)

    def _show_about_desc(self):
        """Display program description in the main frame"""
        # Create a new frame for program description
        frame = self.create_new_frame()
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Add a title at the top
        tk.Label(frame, text=self._get_label('menu_about_desc'), font=("Helvetica", 14, "bold")).grid(row=0, column=0, pady=10)
        
        # Get the about text for current language
        current_lang = self.settings.get('language', DEFAULT_SETTINGS['language'])
        about_desc = ABOUT_TEXTS.get(current_lang, ABOUT_TEXTS['en'])['about_desc']
        
        # Display the description
        text_widget = tk.Text(frame, wrap=tk.WORD, width=70, height=20, bg=frame.cget("bg"))
        text_widget.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        text_widget.insert(tk.END, about_desc)
        text_widget.config(state=tk.DISABLED)  # Make text read-only
        
        self.show_frame(frame)

    def _show_about_author(self):
        """Display author information in the main frame"""
        # Create a new frame for author information
        frame = self.create_new_frame()
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Add a title at the top
        tk.Label(frame, text=self._get_label('menu_about_author'), font=("Helvetica", 14, "bold")).grid(row=0, column=0, pady=10)
        
        # Get the about text for current language
        current_lang = self.settings.get('language', DEFAULT_SETTINGS['language'])
        about_author = ABOUT_TEXTS.get(current_lang, ABOUT_TEXTS['en'])['about_author']
        
        # Display the author information
        text_widget = tk.Text(frame, wrap=tk.WORD, width=70, height=10, bg=frame.cget("bg"))
        text_widget.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        text_widget.insert(tk.END, about_author)
        text_widget.config(state=tk.DISABLED)  # Make text read-only
        
        self.show_frame(frame)

    def prikazi_detalje_knjige(self, naslov, podaci, parent_frame):
        """Модернизовани приказ детаља књиге са напредним UI елементима"""
        # Прикажи индикатор учитавања
        self.update_status(self._get_label('loading_data'))
        self.show_progress(True)
        self.progress_var.set(10)
        
        # Креирај нови фрејм за детаље књиге
        frame = self.create_new_frame()
        
        # Пронађи књигу са датим насловом
        knjiga = None
        for k in podaci:
            if k.get('Наслов') == naslov:
                knjiga = k
                break
                
        if not knjiga:
            self.update_status(f"Књига '{naslov}' није пронађена", error=True)
            self.show_progress(False)
            return
            
        self.progress_var.set(30)
        
        # Креирај модерни хедер
        header_frame = tk.Frame(frame, bg="#2c3e50")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame.grid_columnconfigure(0, weight=1)
        
        # Наслов књиге у хедеру
        title_label = tk.Label(header_frame, text=naslov, font=("Helvetica", 16, "bold"), 
                              fg="white", bg="#2c3e50", anchor="w", padx=10, pady=10)
        title_label.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Статус доступности
        dostupnost = "Доступна" if knjiga.get('Позајмљено') != "Да" else "Није доступна"
        status_color = "#27ae60" if dostupnost == "Доступна" else "#e74c3c"
        status_frame = tk.Frame(header_frame, bg=status_color, padx=10, pady=5)
        status_frame.grid(row=0, column=1, padx=10)
        status_label = tk.Label(status_frame, text=self._get_label('available' if dostupnost == "Доступна" else 'not_available'), 
                               fg="white", bg=status_color, font=("Helvetica", 10, "bold"))
        status_label.pack()
        
        self.progress_var.set(50)
        
        # Креирај таб контролу за организацију информација
        tab_control = ttk.Notebook(frame)
        tab_control.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        frame.grid_rowconfigure(1, weight=1)
        
        # Таб за основне информације
        tab_basic = ttk.Frame(tab_control)
        tab_control.add(tab_basic, text=self._get_label('basic_info'))
        
        # Таб за додатне информације
        tab_additional = ttk.Frame(tab_control)
        tab_control.add(tab_additional, text=self._get_label('additional_info'))
        
        # Таб за информације о позајмици (ако је књига позајмљена)
        if dostupnost == "Није доступна":
            tab_loan = ttk.Frame(tab_control)
            tab_control.add(tab_loan, text=self._get_label('loan_info'))
        
        # Попуни основне информације
        basic_info_frame = ttk.LabelFrame(tab_basic, text=self._get_label('book_info'))
        basic_info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Креирај мрежу за основне информације
        row = 0
        fields = ["Наслов", "Писац", "Година издавања", "Жанр", "Серијал"]
        for field in fields:
            ttk.Label(basic_info_frame, text=f"{field}:", font=("Helvetica", 10, "bold")).grid(
                row=row, column=0, sticky="w", padx=10, pady=5)
            
            # За поље "Писац" можемо имати више аутора
            if field == "Писац" and knjiga.get(field):
                authors = knjiga.get(field).split("; ")
                authors_frame = ttk.Frame(basic_info_frame)
                authors_frame.grid(row=row, column=1, sticky="w", padx=10, pady=5)
                
                for i, author in enumerate(authors):
                    author_label = ttk.Label(authors_frame, text=author)
                    author_label.grid(row=i, column=0, sticky="w")
                    
                    # Додај дугме за приказ свих књига овог аутора
                    author_btn = ttk.Button(authors_frame, text="📚", width=2, 
                                          command=lambda a=author: self.pretrazi_po_piscu(a))
                    author_btn.grid(row=i, column=1, padx=5)
                    ToolTip(author_btn, f"Прикажи све књиге аутора: {author}")
            else:
                value = knjiga.get(field, "")
                ttk.Label(basic_info_frame, text=value).grid(
                    row=row, column=1, sticky="w", padx=10, pady=5)
            row += 1
        
        # Попуни додатне информације
        additional_info_frame = ttk.LabelFrame(tab_additional, text=self._get_label('additional_info'))
        additional_info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        row = 0
        add_fields = ["Колекција", "Издавачи", "ИСБН", "Повез", "Напомена"]
        for field in add_fields:
            field_name = field
            if field == "Издавачи" and "Издавач" in knjiga and not "Издавачи" in knjiga:
                field_name = "Издавач"
                
            ttk.Label(additional_info_frame, text=f"{field}:", font=("Helvetica", 10, "bold")).grid(
                row=row, column=0, sticky="w", padx=10, pady=5)
            
            # За поље "Издавачи" можемо имати више издавача
            if field_name in ["Издавачи", "Издавач"] and knjiga.get(field_name):
                publishers = knjiga.get(field_name).split("; ")
                publishers_frame = ttk.Frame(additional_info_frame)
                publishers_frame.grid(row=row, column=1, sticky="w", padx=10, pady=5)
                
                for i, publisher in enumerate(publishers):
                    ttk.Label(publishers_frame, text=publisher).grid(row=i, column=0, sticky="w")
            else:
                value = knjiga.get(field_name, "")
                ttk.Label(additional_info_frame, text=value).grid(
                    row=row, column=1, sticky="w", padx=10, pady=5)
            row += 1
        
        # Ако је књига позајмљена, попуни информације о позајмици
        if dostupnost == "Није доступна":
            loan_info_frame = ttk.LabelFrame(tab_loan, text=self._get_label('loan_info'))
            loan_info_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            loan_fields = ["Особа", "Датум позајмице", "Рок враћања", "Напомена"]
            loan_data = self._get_loan_data(naslov)
            
            if loan_data:
                for i, field in enumerate(loan_fields):
                    ttk.Label(loan_info_frame, text=f"{field}:", font=("Helvetica", 10, "bold")).grid(
                        row=i, column=0, sticky="w", padx=10, pady=5)
                    ttk.Label(loan_info_frame, text=loan_data.get(field, "")).grid(
                        row=i, column=1, sticky="w", padx=10, pady=5)
            else:
                ttk.Label(loan_info_frame, text="Нема доступних информација о позајмици.").grid(
                    row=0, column=0, columnspan=2, padx=10, pady=20)
        
        self.progress_var.set(80)
        
        # Дугмад за акције
        actions_frame = ttk.Frame(frame)
        actions_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        # Дугме за измену књиге
        edit_btn = self._create_button_with_icon(actions_frame, 'edit_book', 
                                             lambda: self.otvori_izmenu(naslov), style="Modern.TButton")
        edit_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # Дугме за брисање књиге
        delete_btn = self._create_button_with_icon(actions_frame, 'delete_book', 
                                               lambda: self._confirm_delete_book(naslov), style="Modern.TButton")
        delete_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Дугме за позајмицу/враћање књиге
        if dostupnost == "Доступна":
            loan_btn = self._create_button_with_icon(actions_frame, 'loan_book', 
                                                 lambda: self._loan_book(naslov), style="Modern.TButton")
            loan_btn.grid(row=0, column=2, padx=5, pady=5)
        else:
            return_btn = self._create_button_with_icon(actions_frame, 'return_book', 
                                                   lambda: self._return_book(naslov), style="Modern.TButton")
            return_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Дугме за повратак на претходни приказ
        back_btn = self._create_button_with_icon(actions_frame, 'back', 
                                             lambda: self.show_frame(parent_frame), style="Modern.TButton")
        back_btn.grid(row=0, column=3, padx=5, pady=5)
        
        self.progress_var.set(100)
        self.update_status(self._get_label('data_loaded'))
        self.show_progress(False)
        
        # Прикажи фрејм
        self.show_frame(frame)
    
    def _get_loan_data(self, naslov):
        """Dobavlja informacije o pozajmici knjige"""
        try:
            return bib.pretraga_pozajmica(self.putanja, naslov)
        except Exception as e:
            print(f"[DEBUG] Greska pri dobaljivanju informacija o pozajmici: {e}")
            return None
    
    def _confirm_delete_book(self, naslov):
        """Потврда брисања књиге"""
        odgovor = messagebox.askyesno("Потврда", f"Да ли сте сигурни да желите да обришете књигу '{naslov}'?")
        if odgovor and bib.obrisi_knjigu(self.putanja, naslov):
            messagebox.showinfo("Успех", "Књига је успешно обрисана.")
            self.go_back()
        elif odgovor:
            messagebox.showerror("Грешка", "Књига није пронађена или је дошло до грешке при брисању.")
    
    def _loan_book(self, naslov):
        """Отвара дијалог за позајмицу књиге"""
        # Креирање дијалога за позајмицу књиге
        loan_dialog = tk.Toplevel(self.root)
        loan_dialog.title(self.translations.get('loan_book'))
        loan_dialog.geometry("400x250")
        loan_dialog.resizable(False, False)
        loan_dialog.transient(self.root)  # Поставља модални дијалог
        loan_dialog.grab_set()  # Модални дијалог
        
        # Центрирање дијалога
        self._center_window(loan_dialog)
        
        # Креирање оквира за унос података
        frame = ttk.Frame(loan_dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Наслов књиге (само приказ)
        ttk.Label(frame, text=self.translations.get('title') + ":", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        ttk.Label(frame, text=naslov).grid(row=0, column=1, sticky="w", pady=5)
        
        # Поље за унос особе која позајмљује
        ttk.Label(frame, text=self.translations.get('loaned_to') + ":", font=("TkDefaultFont", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        borrower_entry = ttk.Entry(frame, width=30)
        borrower_entry.grid(row=1, column=1, sticky="w", pady=5)
        borrower_entry.focus_set()  # Фокус на поље за унос
        
        # Датум позајмице (данашњи датум)
        ttk.Label(frame, text=self.translations.get('loan_date') + ":", font=("TkDefaultFont", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        loan_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        loan_date_entry = ttk.Entry(frame, textvariable=loan_date_var, width=15)
        loan_date_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Очекивани датум враћања (опционо)
        ttk.Label(frame, text=self.translations.get('return_date') + " " + self.translations.get('optional') + ":", font=("TkDefaultFont", 10)).grid(row=3, column=0, sticky="w", pady=5)
        return_date_var = tk.StringVar()
        return_date_entry = ttk.Entry(frame, textvariable=return_date_var, width=15)
        return_date_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        # Напомена (опционо)
        ttk.Label(frame, text=self.translations.get('notes') + " " + self.translations.get('optional') + ":", font=("TkDefaultFont", 10)).grid(row=4, column=0, sticky="w", pady=5)
        notes_text = tk.Text(frame, width=30, height=3)
        notes_text.grid(row=4, column=1, sticky="w", pady=5)
        
        # Дугмад за потврду и отказивање
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Функција за позајмицу књиге
        def confirm_loan():
            borrower = borrower_entry.get().strip()
            if not borrower:
                messagebox.showerror(self.translations.get('error'), self.translations.get('enter_borrower_name'))
                return
            
            try:
                loan_date_str = loan_date_var.get()
                loan_date = datetime.strptime(loan_date_str, "%Y-%m-%d").date() if loan_date_str else None
                
                return_date_str = return_date_var.get()
                return_date = datetime.strptime(return_date_str, "%Y-%m-%d").date() if return_date_str else None
                
                notes = notes_text.get("1.0", tk.END).strip()
                
                # Позајми књигу
                success = bib.pozajmi_knjigu(self.putanja, naslov, borrower, loan_date, return_date, notes)
                if success:
                    messagebox.showinfo(self.translations.get('success'), self.translations.get('book_loaned'))
                    loan_dialog.destroy()
                    # Освежи приказ детаља књиге
                    self.go_back()
                    self.prikazi_detalje_knjige(naslov)
                else:
                    messagebox.showerror(self.translations.get('error'), self.translations.get('error_loaning_book'))
            except ValueError as e:
                messagebox.showerror(self.translations.get('error'), str(e))
        
        # Дугмад за потврду и отказивање
        ttk.Button(btn_frame, text=self.translations.get('confirm'), command=confirm_loan).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=self.translations.get('cancel'), command=loan_dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _return_book(self, naslov):
        """Враћа позајмљену књигу"""
        # Потврда враћања књиге
        odgovor = messagebox.askyesno(
            self.translations.get('confirm'), 
            self.translations.get('confirm_return_book')
        )
        
        if odgovor:
            try:
                # Врати књигу
                success = bib.vrati_knjigu(self.putanja, naslov)
                if success:
                    messagebox.showinfo(self.translations.get('success'), self.translations.get('book_returned'))
                    # Освежи приказ детаља књиге
                    self.go_back()
                    self.prikazi_detalje_knjige(naslov)
                else:
                    messagebox.showerror(self.translations.get('error'), self.translations.get('error_returning_book'))
            except ValueError as e:
                messagebox.showerror(self.translations.get('error'), str(e))
                
    def _center_window(self, window):
        """Центрира прозор на екрану"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def _show_about_program(self):
        """Display program information in the main frame"""
        # Create a new frame for program information
        frame = self.create_new_frame()
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Add a title at the top
        tk.Label(frame, text=self._get_label('menu_about'), font=("Helvetica", 14, "bold")).grid(row=0, column=0, pady=10)
        
        # Get the about text for current language
        current_lang = self.settings.get('language', DEFAULT_SETTINGS['language'])
        about_program = ABOUT_TEXTS.get(current_lang, ABOUT_TEXTS['en'])['about_program']
        
        # Display the program information
        text_widget = tk.Text(frame, wrap=tk.WORD, width=70, height=15, bg=frame.cget("bg"))
        text_widget.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        text_widget.insert(tk.END, about_program)
        text_widget.config(state=tk.DISABLED)  # Make text read-only
        
        self.show_frame(frame)

    def show_help_window(self):
        """Displays the help content in the main frame"""
        # Create a new frame for help content
        frame = self.create_new_frame()
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Add a title at the top
        tk.Label(frame, text=self._get_label('menu_help'), font=("Helvetica", 14, "bold")).grid(row=0, column=0, pady=10)
        
        # Create a scrollable frame for the help content
        help_frame = ScrollableFrame(frame)
        help_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Get the help texts for current language
        current_lang = self.settings.get('language', DEFAULT_SETTINGS['language'])
        help_texts = HELP_TEXTS.get(current_lang, HELP_TEXTS['en'])  # Default to English if not found
        
        # Add help texts to the frame
        for i, (text, description) in enumerate(help_texts):
            # Add the text with proper formatting - use the text as-is without HTML parsing
            label = tk.Label(help_frame.scrollable_frame, text=text, justify=tk.LEFT, wraplength=650, anchor="w")
            label.grid(row=i*2, column=0, sticky="w", padx=5, pady=2)
            
            # Configure the label to render HTML-like formatting with different font
            label.config(font=("Helvetica", 10))
            
            # If there's a description, add it with indentation
            if description:
                desc_label = tk.Label(help_frame.scrollable_frame, text=description, 
                                    justify=tk.LEFT, wraplength=600, anchor="w")
                desc_label.grid(row=i*2+1, column=0, sticky="w", padx=20, pady=2)
                desc_label.config(font=("Helvetica", 9))
        
        self.show_frame(frame)
        
    def show_license(self):
        """Приказ информација о лиценци у главном оквиру"""
        # Креирање новог оквира за садржај лиценце
        frame = self.create_new_frame()
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Додај наслов на врху
        tk.Label(frame, text=self._get_label('menu_license'), font=("Helvetica", 14, "bold")).grid(row=0, column=0, pady=10)
        
        # Креирај оквир са скрол функцијом за садржај лиценце
        license_frame = ScrollableFrame(frame)
        license_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Прочитај садржај фајла лиценце
        license_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LICENSE')
        license_text = ""
        if os.path.exists(license_path):
            try:
                with open(license_path, 'r', encoding='utf-8') as f:
                    license_text = f.read()
            except Exception as e:
                license_text = f"Грешка при читању фајла лиценце: {e}"
        else:
            license_text = "Фајл лиценце није пронађен."
        
        # Прикажи садржај лиценце
        text_widget = tk.Text(license_frame.scrollable_frame, wrap=tk.WORD, width=70, height=20, bg=frame.cget("bg"))
        text_widget.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        text_widget.insert(tk.END, license_text)
        text_widget.config(state=tk.DISABLED)  # Онемогући измену текста
        
        self.show_frame(frame)

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
        """Модернизовани приказ статистике библиотеке са графиконима"""
        # Прикажи индикатор учитавања
        self.update_status("Учитавање статистике...")
        self.show_progress(True)
        self.progress_var.set(10)
        
        # Креирај нови фрејм за статистику
        frame = self.create_new_frame()
        
        # Асинхроно учитавање података и израчунавање статистике
        import threading
        
        def load_stats():
            try:
                # Учитај податке
                data = bib.ucitaj_podatke(self.putanja)
                self.progress_var.set(30)
                
                # Израчунај основне статистике
                total = ukupno_knjiga(data)
                authors = ukupno_autora(data, bib.podeli_pisce)
                genres = broj_zanrova(data)
                series = broj_serijala(data)
                loans = broj_pozajmica(data)
                self.progress_var.set(50)
                
                # Израчунај детаљне статистике
                knjige_zanr = knjige_po_zanru(data)
                knjige_izdavac = knjige_po_izdavacu(data)
                top5 = top_autori(data, bib.podeli_pisce)
                self.progress_var.set(70)
                
                # Ажурирај UI у главној нити
                self.root.after(0, lambda: self._display_statistics(
                    frame, total, authors, genres, series, loans,
                    knjige_zanr, knjige_izdavac, top5
                ))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Грешка при учитавању статистике: {e}", error=True))
                self.root.after(0, lambda: self.show_progress(False))
        
        # Покрени нит за учитавање
        thread = threading.Thread(target=load_stats)
        thread.daemon = True
        thread.start()
        
        # Прикажи фрејм одмах
        self.show_frame(frame)
    
    def _display_statistics(self, frame, total, authors, genres, series, loans, knjige_zanr, knjige_izdavac, top5):
        """Приказује статистику у модерном интерфејсу са графиконима"""
        # Ажурирај прогрес
        self.progress_var.set(80)
        
        # Креирај посебан фрејм за заглавље
        header_frame = tk.Frame(frame)
        header_frame.grid(row=0, column=0, sticky="ew")
        tk.Label(header_frame, text=self._get_label('statistics'), 
                font=("Helvetica", 16, "bold")).grid(row=0, column=0, pady=10, sticky="ew")
        
        # Таб контрола са модерним изгледом
        tab_control = ttk.Notebook(frame)
        tab_control.grid(row=1, column=0, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Додај посебан ред за дугме "Назад" - биће додато касније у show_frame методи
        # Ово спречава додавање дугмета испод табова
        back_button_frame = tk.Frame(frame)
        back_button_frame.grid(row=2, column=0, sticky="w", pady=10)
        frame.grid_rowconfigure(2, weight=0)
        
        # --- Опште статистике са графиконом ---
        tab_opste = ttk.Frame(tab_control)
        tab_control.add(tab_opste, text=self._get_label('tab_general'))
        tab_opste.grid_columnconfigure(0, weight=1)
        tab_opste.grid_columnconfigure(1, weight=1)
        tab_opste.grid_rowconfigure(5, weight=1)  # За графикон
        
        # Приказ основних статистика у модерном стилу
        stats_frame = ttk.LabelFrame(tab_opste, text=self._get_label('general_stats'))
        stats_frame.grid(row=0, column=0, rowspan=5, sticky="nsew", padx=10, pady=10)
        
        for idx, (label, val) in enumerate([
            (self._get_label('stat_total_books'), total),
            (self._get_label('stat_total_authors'), authors),
            (self._get_label('stat_genres'), genres),
            (self._get_label('stat_series'), series),
            (self._get_label('stat_loans'), loans)
        ]):
            ttk.Label(stats_frame, text=f"{label}:", anchor='w').grid(row=idx, column=0, sticky="w", padx=10, pady=5)
            value_label = ttk.Label(stats_frame, text=str(val), anchor='w')
            value_label.grid(row=idx, column=1, sticky="w", padx=10, pady=5)
            # Додај стилизацију за вредности
            if idx == 0:  # Укупан број књига
                value_label.configure(font=("Helvetica", 10, "bold"))
        
        # Графикон доступности књига
        if Figure:
            chart_frame = ttk.LabelFrame(tab_opste, text=self._get_label('availability_chart'))
            chart_frame.grid(row=0, column=1, rowspan=5, sticky="nsew", padx=10, pady=10)
            
            labels_chart = [self._get_label('available'), self._get_label('loaned')]
            sizes = [total-loans, loans]
            colors = ['#4CAF50', '#FFC107']  # Зелена и жута
            
            fig = Figure(figsize=(4, 3), dpi=100)
            ax = fig.add_subplot(111)
            wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%', 
                                             startangle=90, colors=colors)
            ax.axis('equal')  # Једнаке пропорције за кружни изглед
            
            # Додај легенду
            ax.legend(wedges, labels_chart, title=self._get_label('status'),
                     loc="center left", bbox_to_anchor=(0.9, 0, 0.5, 1))
            
            # Побољшај изглед текста процената
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # --- По жанру са графиконом ---
        tab_zanr = ttk.Frame(tab_control)
        tab_control.add(tab_zanr, text=self._get_label('tab_genre'))
        tab_zanr.grid_columnconfigure(0, weight=1)
        tab_zanr.grid_columnconfigure(1, weight=1)
        
        # Листа жанрова
        zanr_frame = ttk.LabelFrame(tab_zanr, text=self._get_label('genres_list'))
        zanr_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Креирај скроловану листу жанрова
        zanr_scroll = ScrollableFrame(zanr_frame)
        zanr_scroll.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        for idx, (zanr, br) in enumerate(sorted(knjige_zanr.items(), key=lambda x: x[1], reverse=True)):
            ttk.Label(zanr_scroll.scrollable_frame, text=f"{zanr}:", anchor='w').grid(row=idx, column=0, sticky="w", padx=10, pady=2)
            ttk.Label(zanr_scroll.scrollable_frame, text=str(br), anchor='w').grid(row=idx, column=1, sticky="w", padx=10, pady=2)
        
        # Графикон жанрова (top 5)
        if Figure and knjige_zanr:
            chart_frame = ttk.LabelFrame(tab_zanr, text=self._get_label('top_genres_chart'))
            chart_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
            
            # Узми 5 најчешћих жанрова
            top_zanrovi = sorted(knjige_zanr.items(), key=lambda x: x[1], reverse=True)[:5]
            labels = [zanr for zanr, _ in top_zanrovi]
            values = [br for _, br in top_zanrovi]
            
            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)
            bars = ax.bar(labels, values, color='#2196F3')
            
            # Додај вредности изнад стубића
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}', ha='center', va='bottom')
            
            ax.set_ylabel(self._get_label('book_count'))
            ax.set_title(self._get_label('top_genres'))
            fig.tight_layout()
            
            # Ротирај лабеле за боље уклапање
            plt = ax.get_xticklabels()
            for label in plt:
                label.set_rotation(45)
                label.set_ha('right')
            
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # --- По издавачу ---
        tab_izdavac = ttk.Frame(tab_control)
        tab_control.add(tab_izdavac, text=self._get_label('tab_publisher'))
        
        # Листа издавача
        izdavac_frame = ttk.LabelFrame(tab_izdavac, text=self._get_label('publishers_list'))
        izdavac_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Креирај скроловану листу издавача
        izdavac_scroll = ScrollableFrame(izdavac_frame)
        izdavac_scroll.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        for idx, (izd, br) in enumerate(sorted(knjige_izdavac.items(), key=lambda x: x[1], reverse=True)):
            ttk.Label(izdavac_scroll.scrollable_frame, text=f"{izd}:", anchor='w').grid(row=idx, column=0, sticky="w", padx=10, pady=2)
            ttk.Label(izdavac_scroll.scrollable_frame, text=str(br), anchor='w').grid(row=idx, column=1, sticky="w", padx=10, pady=2)
        
        # --- Топ 5 аутора са графиконом ---
        tab_autori = ttk.Frame(tab_control)
        tab_control.add(tab_autori, text=self._get_label('tab_top_authors'))
        tab_autori.grid_columnconfigure(0, weight=1)
        tab_autori.grid_columnconfigure(1, weight=1)
        
        # Листа топ аутора
        autori_frame = ttk.LabelFrame(tab_autori, text=self._get_label('top_authors_list'))
        autori_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        for idx, (autor, br) in enumerate(top5):
            ttk.Label(autori_frame, text=f"{idx+1}. {autor}:", anchor='w').grid(row=idx, column=0, sticky="w", padx=10, pady=2)
            ttk.Label(autori_frame, text=str(br), anchor='w').grid(row=idx, column=1, sticky="w", padx=10, pady=2)
        
        # Графикон топ аутора
        if Figure and top5:
            chart_frame = ttk.LabelFrame(tab_autori, text=self._get_label('top_authors_chart'))
            chart_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
            
            labels = [autor for autor, _ in top5]
            values = [br for _, br in top5]
            
            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            # Хоризонтални бар график за боље приказивање дугих имена аутора
            bars = ax.barh(labels, values, color='#9C27B0')  # Љубичаста боја
            
            # Додај вредности на крају сваког бара
            for i, v in enumerate(values):
                ax.text(v + 0.1, i, str(v), va='center')
            
            ax.set_xlabel(self._get_label('book_count'))
            ax.set_title(self._get_label('top_authors'))
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Сакриј прогрес бар и ажурирај статус
        self.progress_var.set(100)
        self.update_status(self._get_label('stats_loaded'))
        self.root.after(500, lambda: self.show_progress(False))

    def _compute_availability(self, knjига):
        """Одређује статус доступности књиге."""
        pos = knjига.get("Позајмљена", "").strip()
        vra = knjига.get("Враћена", "").strip()
        if not pos or vra:
            return "Доступна"
        return "Није доступна"

    def _show_loan_details(self, naslov):
        """Приказује детаље о позајмици за књигу."""
        details = bib.pretraga_pозajmica(self.putanja, naslov)
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
                    if bib.sacuvaj_podatке(self.putanja, data):
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
        fields = ["Наслов", "Писац", "Година издавања", "Жанр", "Серијал", "Колекција", "Издавачи", "ИСБН", "Повез", "Напомена"]
        entries = {}

        def create_field(field, row):
            """Helper function to create input fields."""
            tk.Label(frame, text=f"{field}:").grid(row=row, column=0, padx=5, pady=5)
            if field == "Писац":
                entries[field] = self._create_scrollable_section(frame, row, pisci, "authors")
            elif field == "Издавачи":
                entries[field] = self._create_scrollable_section(frame, row, izdavac, "publishers")
            elif field in ["Жанр", "Повез"]:
                combo = ttk.Combobox(frame, values=zanr if field == "Жанр" else povez)
                combo.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
                entries[field] = combo
            else:
                entry = tk.Entry(frame)
                entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
                entries[field] = entry

        for i, field in enumerate(fields):
            create_field(field, i)

        def sacuvaj():
            nova_knjiga = {}
            for field in fields:
                if field == "Писац":
                    # Prikupljamo sve unesene pisce
                    authors = [e.get() for e in entries[field] if e.get().strip()]
                    nova_knjiga[field] = "; ".join(authors)
                elif field == "Издавачи":
                    # Prikupljamo sve unesene izdavače
                    publishers = [e.get() for e in entries[field] if e.get().strip()]
                    # Čuvamo u polje "Издавач" za kompatibilnost sa CSV
                    nova_knjiga["Издавач"] = "; ".join(publishers)
                else:
                    # Za ostala polja uzimamo vrednost direktno
                    if hasattr(entries[field], 'get'):
                        nova_knjiga[field] = entries[field].get()
                    else:
                        nova_knjiga[field] = entries[field]
            
            # Dodajemo knjigu
            if nova_knjiga["Наслов"]:
                uspeh = bib.dodaj_knjigu(self.putanja, nova_knjiga)
                if uspeh:
                    messagebox.showinfo(self._get_label('success'), self._get_label('book_added'))
                    # Ažuriramo liste za žanr, izdavače i pisce
                    if hasattr(bib, 'inicijalizuj_podatke'):
                        azurirani_podaci = bib.inicijalizuj_podatke(self.putanja)
                        global zanr, izdavac, pisci
                        zanr = azurirani_podaci['zanr']
                        izdavac = azurirani_podaci['izdavac']
                        pisci = azurirani_podaci['pisci']
                    self.go_back()
                else:
                    messagebox.showerror(self._get_label('error'), self._get_label('error_adding_book'))
            else:
                messagebox.showerror(self._get_label('error'), self._get_label('title_required'))

        tk.Button(frame, text=self._get_label('save'), command=sacuvaj).grid(row=len(fields), column=0, columnspan=2, pady=10, sticky="ew")
        self.show_frame(frame)

    def _create_scrollable_section(self, parent, row, values, label):
        """Helper function to create a scrollable section for authors or publishers."""
        section = tk.LabelFrame(parent, text=self._get_label(label), padx=2, pady=2)
        section.grid(row=row, column=1, padx=5, pady=5, sticky="nsew")
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        section.grid_rowconfigure(0, weight=1)
        section.grid_columnconfigure(0, weight=1)
        
        # Scrollable frame za unose
        scrollable = ScrollableFrame(section, height=120)
        scrollable.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        container = scrollable.get_frame()
        container.grid_columnconfigure(1, weight=1)
        entries = []

        def add_field(name=""):
            row = len(entries)
            btn_remove = ttk.Button(container, text="-", width=2, command=lambda r=row: remove_field(r))
            btn_remove.grid(row=row, column=0, padx=2, pady=2, sticky="nw")
            entry = ttk.Combobox(container, values=values, width=25)
            entry.grid(row=row, column=1, padx=2, pady=2, sticky="ew")
            entry.insert(0, name)
            container.grid_rowconfigure(row, weight=0)
            entries.append(entry)

        def remove_field(row):
            if 0 <= row < len(entries):
                entries[row].destroy()
                # Pronađi i uništi dugme za brisanje
                for widget in container.grid_slaves(row=row, column=0):
                    if isinstance(widget, ttk.Button):
                        widget.destroy()
                entries.pop(row)
                # Ažuriraj pozicije preostalih polja
                for i, entry in enumerate(entries):
                    btn = None
                    for widget in container.grid_slaves(row=i, column=0):
                        if isinstance(widget, ttk.Button):
                            btn = widget
                            break
                    if btn:
                        btn.grid(row=i, column=0, padx=2, pady=2, sticky="nw")
                    entry.grid(row=i, column=1, padx=2, pady=2, sticky="ew")
            else:
                print(f"[DEBUG] Pokušaj brisanja nevalidnog polja: {row}")

        # Dodaj prvo polje
        add_field()
        
        # Dodaj sekciju za dodavanje novog polja
        add_section_frame = tk.Frame(section)
        add_section_frame.grid(row=1, column=0, sticky="ew", pady=(5,0))
        add_section_frame.grid_columnconfigure(0, weight=1)
        new_entry = ttk.Combobox(add_section_frame, values=values, width=25)
        new_entry.grid(row=0, column=0, padx=2, sticky="ew")
        
        # Funkcija za dodavanje novog polja iz unosa
        def add_new_from_entry():
            name = new_entry.get().strip()
            if name:
                add_field(name)
                new_entry.delete(0, tk.END)
        
        # Dugme za dodavanje novog polja
        btn_add = ttk.Button(add_section_frame, text="+", width=2, command=add_new_from_entry)
        btn_add.grid(row=0, column=1, padx=2)
        
        return entries
    
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
        # Креирамо дугме за брисање са иконом
        delete_btn = self._create_button_with_icon(frame, 'delete_book', obrisi)
        delete_btn.grid(row=2, column=0, pady=5)
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
                if bib.sacuvaj_podatке(self.putanja, data):
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
    # Ensure all required data is loaded
    global zanr, izdavac, povez, pisci
    
    # Initialize data from CSV file
    if hasattr(bib, 'inicijalizuj_podatке'):  # Fixed function name
        podaci = bib.inicijalизуј_podatке(putanja_do_bcsv)  # Fixed function call
        zanr = podaci['zanr']
        izdavac = podaci['izdavac']
        povez = podaci['povez']
        pisci = podaci['pisci']
    
    # Start main window
    root = tk.Tk()
    app = BibliotekaGUI(root, putanja_do_bcsv)
    root.mainloop()