# Implementační dokumentace 1. části projektu z IPP 2022
Autor: Štěpán Bílek

Login: xbilek25

## 1. Syntaktický analyzátor ```parse.php```
Úkolem syntaktického analyzátoru je zpracování a kontrolá kódu zapsaného v jazyce IPPcode22. Výstupem je struktura v jazyce XML, která obsahuje informace o vstupním kódu.

### 1.1 Zpracování argumentů
Zpracování argumentů probíhá pomocí jednoduché podmínky - pokud je skripto spouštěn s více než jedním argumentem, nebo s jedním argumentem, jiným než ```--help```, vrátí skript chybu, jinak pracuje dále.

### 1.2 Načítání vstupu
Načítání vstupu probíhá v cyklu while po jednotlívých řádcích. Pokud je řádek prázdný, nebo obsahuje pouze komentář, je v cyklu přeskočen. Při~průchodu prvním validním řádkem je provedena kontrola hlavičky. Toho aby se hlavička kontrolovala pouze při prvních průchodu se dosahuje přepsáním booleové globální proměnné ```header```. Každý další řádek je při načtení zbaven zbytečných bílých znaků a komentářů.

### 1.3 Zpracování instrukcí
Instrukce zbavené komentářů a zbytečných bílých znaků jsou pomocí funkce ```explode()``` rozděleny na jednotlivé prvky pole. První prvek tohoto pole vždy tvoří instrukce a podle druhu insturkce je vždy kontrolován počet a sémantika argumentů
