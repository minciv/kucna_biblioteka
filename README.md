## -*- coding: utf-8 -*-
## @Author  : minciv
## @File    : README.md
## @Software: Windsurf
## @Description: Датотека за упознавање са програмом Кућна Библиотека


# Кућна библиотека (Home Library) (v0.0.01.02)

Python GUI апликација за вођење евиденције о књигама, ауторима, серијалима, издавачима и позајмицама у кућној библиотеци.

## Лиценца

Овај пројекат је под CC BY-NC 4.0 лиценцом – види [LICENSE](LICENSE) за детаље.
Фајл Biblioteka.csv.example је под CC BY-Zero 1.0.

**CC BY-NC 4.0 (Creative Commons Attribution-NonCommercial 4.0 International)**

- Слободно користите, делите и мењате овај софтвер у некомерцијалне сврхе.
- Морате навести аутора (атрибуција).
- Није дозвољена комерцијална употреба (нпр. продаја, интеграција у комерцијални производ, наплата услуге).
- Пуни текст лиценце: https://creativecommons.org/licenses/by-nc/4.0/
- Пуни текст лиценце за фајл `Biblioteka.csv.example`: https://creativecommons.org/licenses/by/1.0/

**ENGLISH SUMMARY:**

- Free to use, share, and modify for non-commercial purposes.
- Attribution is required (credit the author).
- Commercial use is NOT allowed (no selling, no use in paid/commercial products or services).
- Full license text: https://creativecommons.org/licenses/by-nc/4.0/
- Full license text for file `Biblioteka.csv.example`: https://creativecommons.org/licenses/by/1.0/

## Главне функције
- Додавање, измена и брисање књига
- Претрага по разним критеријумима
- Управљање серијалима, жанровима, издавачима
- Позјамице са историјом
- Извоз/увоз (CSV, JSON, Excel)
- Статистика у табовима (жанр, издавач, топ аутори, дијаграм)
- Вишејезички интерфејс (српски ћирилица/латиница, енглески, француски, руски, шпански, немачки, италијански)
- Аутоматски backup CSV-а (до 10 последњих)

## Main features
- Add, edit, and delete books
- Search by various criteria
- Manage series, genres, publishers
- Loan tracking with history
- Export/Import (CSV, JSON, Excel)
- Statistics in tabs (genre, publisher, top authors, chart)
- Multilingual interface (Serbian Cyrillic/Latin, English, French, Russian, Spanish, German, Italian)
- Automatic CSV backup (up to 10 latest)

## How to run / Како покренути
1. Clone the repository:/ Клонирај репо:
   ```bash
   git clone https://github.com/korisnik/kucna-biblioteka.git
   cd kucna-biblioteka
   ```
2. Create a virtual environment and install dependencies (if you are using): /Креирај виртуелно окружење и инсталирај зависности (ако користиш):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the application:/Покретање апликације:
   ```bash
   python kucna_biblioteka.py
   ```

## Initial data / Почетни подаци
- Фајл `Biblioteka.csv.example` садржи пример структуре и неколико тест књига.
- За свој рад, копирај га као `Biblioteka.csv`.
- **Не upload-уј свој приватни CSV у јавни репо!**

## About the author / О аутору
minciv  
minciv@protonmail.com

### 🇷🇸 Српски (ћирилица)
Пензионер коме је досадило да седи и ништа неради
па седе и научи Python и написа програмчић
за праћење књига и позајмица
јер му је досадило да се присећа
коме и када је позајмио књигу

**Ово је за оне који "Слабо памте, а брзо заборављају"**

### 🇷🇸 Srpski (latinica)
Penzioner kome je dosadilo da sedi i ništa neradi
pa sede i nauči Python i napisa programčić
za praćenje knjiga i pozajmica
jer mu je dosadilo da se priseća
kome i kada je pozajmio knjigu

**Ovo je za one koji "Slabo pamte, a brzo zaboravljaju"**

### 🇬🇧 English
Retired guy who got tired of just sitting and doing nothing
so he sat down, learned Python and wrote a little program
for tracking books and loans
because he was tired of trying to remember
to whom and when he lent a book

**This is for those who "Remember little and forget quickly"**

### 🇫🇷 Français
Un retraité qui en avait assez de rester assis à ne rien faire
alors il s'est assis, a appris Python et a écrit un petit programme
pour suivre les livres et les prêts
parce qu'il en avait assez d'essayer de se souvenir
à qui et quand il avait prêté un livre

**C'est pour ceux qui "Se souviennent peu et oublient vite"**

### 🇷🇺 Русский
Пенсионер, которому надоело сидеть и ничего не делать,
поэтому он сел, выучил Python и написал небольшую программу
для отслеживания книг и займов,
потому что ему надоело пытаться вспомнить,
кому и когда он одолжил книгу

**Это для тех, кто "Мало помнит и быстро забывает"**

### 🇪🇸 Español
Un jubilado que se cansó de estar sentado sin hacer nada
así que se sentó, aprendió Python y escribió un pequeño programa
para seguir libros y préstamos
porque estaba cansado de tratar de recordar
a quién y cuándo prestó un libro

**Esto es para aquellos que "Recuerdan poco y olvidan rápido"**

### 🇩🇪 Deutsch
Ein Rentner, der es satt hatte, nur herumzusitzen und nichts zu tun,
also setzte er sich hin, lernte Python und schrieb ein kleines Programm
zur Verfolgung von Büchern und Ausleihen,
weil er es satt hatte, sich zu erinnern,
wem und wann er ein Buch ausgeliehen hatte

**Dies ist für diejenigen, die "Wenig erinnern und schnell vergessen"**

### 🇮🇹 Italiano
Un pensionato stanco di stare seduto a non fare niente
quindi si è seduto, ha imparato Python e ha scritto un piccolo programma
per tenere traccia di libri e prestiti
perché era stanco di cercare di ricordare
a chi e quando aveva prestato un libro

**Questo è per coloro che "Ricordano poco e dimenticano velocemente"**

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

**Слободно шаљи pull request-ове, пријави баг или предложи нову функцију!**

**Free to send pull requests, report bugs or suggest new features!**