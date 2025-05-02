import tkinter as tk
from tkinter import messagebox
from Biblioteka import ucitaj_podatke, dodaj_knjigu, obrisi_knjigu, pretraga, pretraga_pozajmica

# Функција за приказ свих књига
def prikazi_knjige(put_do_bibcsv):
    # Приказује све књиге из библиотеке у новом прозору
    podaci = ucitaj_podatke(put_do_bibcsv)
    if not podaci:
        messagebox.showinfo("Информација", "Нема доступних књига.")
        return

    prikaz = tk.Toplevel()
    prikaz.title("Све књиге")
    for knjiga in podaci:
        tekst = "\n".join([f"{kljuc}: {vrednost}" for kljuc, vrednost in knjiga.items()])
        tk.Label(prikaz, text=tekst, justify="left", anchor="w").pack(padx=10, pady=5)

# Функција за додавање нове књиге
def dodaj_knjigu_gui(put_do_bibcsv):
    def sacuvaj():
        # Чува нову књигу у библиотеку
        naslov = naslov_entry.get()
        pisac = pisac_entry.get()
        godina = godina_entry.get()
        zanr = zanr_entry.get()
        serijal = serijal_entry.get()
        kolekcija = kolekcija_entry.get()
        izdavac = izdavac_entry.get()
        isbn = isbn_entry.get()
        povez = povez_entry.get()
        napomena = napomena_entry.get()

        nova_knjiga = {
            "Наслов": naslov,
            "Писац": pisac,
            "Година издавања": godina,
            "Жанр": zanr,
            "Серијал": serijal,
            "Колекција": kolekcija,
            "Издавач": izdavac,
            "ИСБН": isbn,
            "Повез": povez,
            "Напомена": napomena
        }

        dodaj_knjigu(put_do_bibcsv)
        messagebox.showinfo("Успех", "Књига је успешно додата.")
        dodavanje.destroy()

    dodavanje = tk.Toplevel()
    dodavanje.title("Додај књигу")

    tk.Label(dodavanje, text="Наслов:").grid(row=0, column=0, padx=5, pady=5)
    naslov_entry = tk.Entry(dodavanje)
    naslov_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(dodavanje, text="Писац:").grid(row=1, column=0, padx=5, pady=5)
    pisac_entry = tk.Entry(dodavanje)
    pisac_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(dodavanje, text="Година издавања:").grid(row=2, column=0, padx=5, pady=5)
    godina_entry = tk.Entry(dodavanje)
    godina_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(dodavanje, text="Жанр:").grid(row=3, column=0, padx=5, pady=5)
    zanr_entry = tk.Entry(dodavanje)
    zanr_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(dodavanje, text="Серијал:").grid(row=4, column=0, padx=5, pady=5)
    serijal_entry = tk.Entry(dodavanje)
    serijal_entry.grid(row=4, column=1, padx=5, pady=5)

    tk.Label(dodavanje, text="Колекција:").grid(row=5, column=0, padx=5, pady=5)
    kolekcija_entry = tk.Entry(dodavanje)
    kolekcija_entry.grid(row=5, column=1, padx=5, pady=5)

    tk.Label(dodavanje, text="Издавач:").grid(row=6, column=0, padx=5, pady=5)
    izdavac_entry = tk.Entry(dodavanje)
    izdavac_entry.grid(row=6, column=1, padx=5, pady=5)

    tk.Label(dodavanje, text="ИСБН:").grid(row=7, column=0, padx=5, pady=5)
    isbn_entry = tk.Entry(dodavanje)
    isbn_entry.grid(row=7, column=1, padx=5, pady=5)

    tk.Label(dodavanje, text="Повез:").grid(row=8, column=0, padx=5, pady=5)
    povez_entry = tk.Entry(dodavanje)
    povez_entry.grid(row=8, column=1, padx=5, pady=5)

    tk.Label(dodavanje, text="Напомена:").grid(row=9, column=0, padx=5, pady=5)
    napomena_entry = tk.Entry(dodavanje)
    napomena_entry.grid(row=9, column=1, padx=5, pady=5)

    tk.Button(dodavanje, text="Сачувај", command=sacuvaj).grid(row=10, column=0, columnspan=2, pady=10)

# Главна функција
def main():
    put_do_bibcsv = '/home/minciv/Документа/Učenje/Python/Biblioteka/Biblioteka.csv'

    root = tk.Tk()
    root.title("Кућна библиотека")

    tk.Button(root, text="Прикажи све књиге", command=lambda: prikazi_knjige(put_do_bibcsv)).pack(pady=10)
    tk.Button(root, text="Додај нову књигу", command=lambda: dodaj_knjigu_gui(put_do_bibcsv)).pack(pady=10)
    tk.Button(root, text="Излаз", command=root.destroy).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
