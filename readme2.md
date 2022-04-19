Implementační dokumentace k 2. úloze z IPP 2021/2022

Jméno a příjmení: Štěpán Bílek

Login: xbilek25

## 1. Interpret ```interpret.py```
Úkolem skriptu je interpretace kódu jazyka IPPcode22.

### 1.1 Zpracování argumentů
Pro zpracovánní argumentů se využívá knihovna ```argparse```.

### 1.2 Načítání vstupu
Pro načítání vstupu se využívá knihovna  ```xml.etree.ElementTree```. Zpracované instrukce jsou uloženy do seznamu ```instructions```.

### 1.3 Interpretace kódu

#### 1.3.1 Třídy
Pro přístup k instrukcím, proměnným a argumentům slouží tříd ```Instruction```, ```Argument``` a ```Variable```.

#### 1.3.2 Rámce
Všechny rámce jsou realizovány pomocí globálních proměnných. Globální rámec v podobě slovníku ```GF```, dočasný rámec v podobě proměnné ```TF``` a lokální rámec v podobě seznamu ```LF```.

#### 1.3.3 Funkce pro vykonávání instrukcí
Pro každou instrukci je implementována funkce, která ji vykoná. Tyto funkce jsou volány pomocí funkce ```interpret_instruction```, která podle ```opcode``` instrukce na vstupu zavolá odpovídající funkci.

#### 1.3.4 Průchod programem
Průchod programem probíhá ve dvou cyklech. Prvni for cyklus projde všechny instrukce, zkontroluje je pomocí funkce ```check_instruction``` a pokud se jedná o návěští, uloží jej a jeho pozici do slovníku ```labels```. Druhým cyklem je cyklus while, který procház všechny instrukce a každou vykoná pomocí funkce ```interpret_instruction```. Po každé vykonané instrukci se inkrementuje pozice v programu v podobě globální porměnné ```position```.

#### 1.3.5 Skokové instrukce
Skoky jsou vykonávány změnou proměnné ```position``` na pozici odpovídajícícho návěští.
