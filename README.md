# Implementační dokumentace 1. části projektu z IPP 2022
Autor: Štěpán Bílek

Login: xbilek25

## 1. Syntaktický analyzátor ```parse.php```
Úkolem syntaktického analyzátoru je zpracování a kontrola kódu zapsaného v jazyce IPPcode22. Výstupem je struktura v jazyce XML, která obsahuje informace o vstupním kódu.

### 1.1 Zpracování argumentů
Zpracování argumentů probíhá pomocí jednoduché podmínky - pokud je skripto spouštěn s více než jedním argumentem, nebo s jedním argumentem, jiným než ```--help```, vrátí skript chybu, jinak pracuje dále.

### 1.2 Načítání vstupu
Načítání vstupu probíhá v cyklu while po jednotlívých řádcích. Pokud je řádek prázdný, nebo obsahuje pouze komentář, je v cyklu přeskočen. Při průchodu prvním validním řádkem je provedena kontrola hlavičky. Toho aby se hlavička kontrolovala pouze při prvních průchodu se dosahuje přepsáním booleové globální proměnné ```header```. Každý další řádek je při načtení zbaven zbytečných bílých znaků a komentářů.

### 1.3 Zpracování instrukcí
Instrukce zbavené komentářů a zbytečných bílých znaků jsou pomocí funkce ```explode()``` rozděleny na jednotlivé prvky pole. První prvek tohoto pole vždy tvoří instrukce a podle druhu insturkce je vždy kontrolován počet a tvar argumentů argumentů. Kontrolu počtu argumentů zařizuje funkce ```argumentCountCheck()```. Sémantiku kontrolují funkce, které vždy srovnají tvar argumentu odpovídajícím regulárním výrazem pomocí funkce ```preg_match()```. K rozlíšení toho, jestli se jedná o kontrolu hodnoty, nebo proměnné slouží globalní proměná ```variable```. Pořadí instrukcí je zajištěno proměnnou ```instructionNum```, která je nastavena na nulu a s každou iterací se inkrementuje.

### 1.4 Výstup
Výstup je reprezentován globální proměnnou ```output``` do které se nejprve nahraje povinná hlavička. Dále jsou pomocí funkcí konkatenovány jednotlivé instrukce a jejich argumenty. Pokud nebude ve vstupním souboru žádná chyba, ```output``` se vypíše na standardní výstup
