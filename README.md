# Implementační dokumentace 1. části projektu z IPP 2022
Autor: Štěpán Bílek

Login: xbilek25

## 1. Syntaktický analyzátor ```parse.php```
Úkolem syntaktického analyzátoru je zpracování a kontrolá kódu zapsaného v jazyce IPPcode22. Výstupem je struktura v jazyce XML, která obsahuje informace o vstupním kódu.

### 1.1 Zpracování argumentů
Zpracování argumentů probíhá pomocí jednoduché podmínky - pokud je skripto spouštěn s více než jedním argumentem, nebo s jedním argumentem, jiným než ```--help```, vrátí skript chybu, jinak pracuje dále.

#
