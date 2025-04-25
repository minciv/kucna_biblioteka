## -*- coding: utf-8 -*-
## @Author  : minciv
## @File    : README.md
## @Software: Windsurf
## @Description: Датотека за упознавање са програмом Кућна Библиотека


# Кућна библиотека (Home Library)

Python GUI апликација за вођење евиденције о књигама, ауторима, серијалима и позајмицама у кућној библиотеци.

## Лиценца

Овај пројекат је под CC BY-NC 4.0 лиценцом – види [LICENSE](LICENSE) за детаље.

**CC BY-NC 4.0 (Creative Commons Attribution-NonCommercial 4.0 International)**

- Слободно користите, делите и мењате овај софтвер у некомерцијалне сврхе.
- Морате навести аутора (атрибуција).
- Није дозвољена комерцијална употреба (нпр. продаја, интеграција у комерцијални производ, наплата услуге).
- Пуни текст лиценце: https://creativecommons.org/licenses/by-nc/4.0/

**ENGLISH SUMMARY:**

- Free to use, share, and modify for non-commercial purposes.
- Attribution is required (credit the author).
- Commercial use is NOT allowed (no selling, no use in paid/commercial products or services).
- Full license text: https://creativecommons.org/licenses/by-nc/4.0/

## Пример Података

Фајл `Biblioteka.csv.example` садржи примере података о књигама и посвећен је јавном домену под Creative Commons Zero v1.0 Universal License.

## Главне функције
- Додавање, измена и брисање књига
- Претрага по разним критеријумима
- Управљање серијалима, жанровима, издавачима
- Позјамице са историјом
- Извоз/увоз (CSV, JSON, Excel)
- Статистика у табовима (жанр, издавач, топ аутори, дијаграм)
- Вишејезични интерфејс (српски ћирилица/латиница, енглески)
- Аутоматски backup CSV-а (до 10 последњих)

## Како покренути
1. Клонирај репо:
   ```bash
   git clone https://github.com/korisnik/kucna-biblioteka.git
   cd kucna-biblioteka
   ```
2. Креирај виртуелно окружење и инсталирај зависности (ако користиш):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Покрени апликацију:
   ```bash
   python kucna_biblioteka.py
   ```

## Почетни подаци
- Фајл `Biblioteka.csv.example` садржи пример структуре и неколико тест књига.
- За свој рад, копирај га као `Biblioteka.csv`.
- **Не upload-уј свој приватни CSV у јавни репо!**

## О аутору
minciv  
minciv@protonmail.com

Пензионер коме је досадило да седи и ништа неради
па седе и научи Python и написа програмчић
за праћење књига и позајмица
јер му је досадило да се присећа
коме и када је позајмио књигу

# Ово је за оне који "Слабо памте, а брзо заборављају"

---

Retired guy who got tired of just sitting and doing nothing
so he sat down, learned Python and wrote a little program
for tracking books and loans
because he was tired of trying to remember
to whom and when he lent a book

# This is for those who "Remember little and forget quickly"

**Слободно шаљи pull request-ове, пријави баг или предложи нову функцију!**

**Free to send pull requests, report bugs or suggest new features!**
