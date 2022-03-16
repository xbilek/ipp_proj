<?php
ini_set('dispalay_errors', 'stderr');

//globalni promenne

//pro kontrolu hlavicky 
$header = False;

//pro poradi instrukci
$instructionNum = 1;

//pro rozliseni promenne a konstanty
$variable = True;

//pro vystup
$output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
$output.= "<program language=\"IPPcode22\">\n";


// funkce bere jako parametr string, a vraci stejny string s odstranenym komentarem
Function removeComment (string $comLine)
{
    if (strpos($comLine, '#') != NULL)
    {
        return substr($comLine, 0, strpos($comLine, '#'));
    }
    return $comLine;
}

//fukce ktere bere jako parametr poradi instrukce a jeji operacni kod, prida tyto informace ve spravnem xml formatu na vystup
Function addInstruction (int $order, string $opcode)
{
    global $output;
    $output.= "<instruction order=\"";
    $output.= $order;
    $output.= "\" opcode=\"";
    $output.= $opcode;
    $output.= "\">\n";
}

//funkce, ktera prida na vystup XML ukonceni instrukce
Function endInstruction()
{
    global $output;
    $output.= "</instruction>\n";
}

//funkce, ktera bere jako parametry cislo, typ a data argumentu a a prida je na vystup ve spravnem xml fomatu
Function addArgument(int $argNum, string $argType, string $argData)
{
    global $output;
    $output.= "<arg".$argNum." type=\"".$argType."\">".$argData."</arg".$argNum.">\n";
}

//funkce, ktera bere jako parametr pozadovany pocet argumentu a pole argumentu, pokud pocet argumentu nesouhlasi s pozadovanym cislem vrati chybu
Function argumentCountCheck(int $num, array $data)
{
    if($num != count($data) - 1)
    {
        fwrite(STDERR, "Spatny pocet argumentu intrukce \n");
        exit(23);
    }
}

//funkce, ktera bere jako parametr promennou, srovna ji s odpovidajicim regularnim vyrazem a pokud nesouhlasi, vrati chybu
Function varCheck(string $var)
{
    if (!preg_match("/^(LF|TF|GF)@[a-zA-Z_$&%*!?-][a-zA-Z0-9_$&%*!?-]*$/", $var))
    {
        fwrite(STDERR, "Spatne zapsana promenna \n");
        exit(23);
    }
}

//funkce, ktera bere jako parametr navesti, srovna ho s odpovidajicim regularmin vyrazem a pokud nesouhlasi, vrati chybu
Function labelCheck(string $label)
{
    if (!preg_match("/^[a-zA-Z_$&%*!?-][a-zA-Z0-9_$&%*!?-]*$/", $label))
    {
        fwrite(STDERR, "Spatne zapsane navesti \n");
        exit(23);
    }

}

//funkce, ktera bere jako parametr symbol, srovna ho s odpovidajicim regularmin vyrazem a pokud nesouhlasi, vrati chybu
Function symbolCheck(string $symbol)
{
    if (!(preg_match("/^(GF|LF|TF|bool|nil)@[a-zA-Z_$&%*!?-][\S]*/", $symbol) || preg_match("/^string@[\S]*$/", $symbol) ||preg_match("/^int@[+-]{0,1}[\d]{1,}$/", $symbol)))
    {
        fwrite(STDERR, "Spatne zapsany symbol \n");
        exit(23);
    }
}

//funkce, ktera bere jako parametr typ, pokud je spatne zapsany, vrati chybu
Function typeCheck(string $type)
{
    if (!($type == "int" || $type == "string" || $type == "bool"))
    {
    fwrite(STDERR, "Spatne zapsany symbol \n");
        exit(23);
    }
}

//funkce, ktera bere jako parametr symbol, vrati jeho typ
Function get_Type(string $symbol)
{
    if (strpos($symbol, '@') != NULL)
    {
        return substr($symbol, 0, strpos($symbol, '@'));
    }
    return $symbol;
}

//funkce, ktera bere jako parametr symbol a vrati promennou ve spravnem tvaru
Function toVar($symbol)
{
    global $variable;
    if($symbol == "GF" || $symbol == "LF" || $symbol == "TF")
    {
        $symbol = "var";
        $variable = True;
        return $symbol;
    }
    $variable = False;
    return $symbol;
}

//funkce ktera bere jako parametr symbol, vrati jeho hodnotu
Function getValue(string $symbol)
{
    global $variable;
    if($variable)
    {
        return $symbol;
    }
    if (strpos($symbol, '@') != NULL)
    {
        return substr($symbol, strpos($symbol, '@')+1, strlen($symbol));
    }
    return $symbol;
}


//zpracovani argumentu
if($argc == 2)
{
    if($argv[1] == "--help")
    {
        echo "Pouziti: parser.php [argumenty] <VstupniSoubor\n";
        exit(0);
    }
    else
    {
        fwrite(STDERR, "Spatne argumenty\n");
        exit(10);
    }
}
else if($argc > 2)
{
        fwrite(STDERR, "Spatne argumenty\n");
        exit(10);
}



//hlavni smycka
while($line = fgets(STDIN))
{   
    //odstarneni prazdnych radku a radku obsahujicich pouze komentar
    if ($line == "\n" || $line[0] == '#')
    {
        continue;
    }

    //kontrola hlavicky
    if(!$header)
    {
        $line = rtrim(trim(removeComment($line), "\n"));
        if($line == ".IPPcode22")
        {
            $header = true;
            continue;
        }
        else
        {
            fwrite(STDERR, "Chybejici hlavicka \n");
            exit(21);
        }
    }

    //odsratneni prebytecnych bilych mezer, znaku novych radku a kometnaru
    $normalizedLine = explode(' ', rtrim(removeComment(trim(ltrim($line)), "\n")));

    //switch ktery zpracovava kod podle instrukci na vstupu
    switch(strtoupper($normalizedLine[0]))
    {

        case 'CREATEFRAME':
        case 'PUSHFRAME':
        case 'POPFRAME':
        case 'RETURN':
        case 'BREAK':
        {
            argumentCountCheck(0, $normalizedLine);
            addInstruction($instructionNum, $normalizedLine[0]);
            endInstruction();
            break;
        }
        case 'DEFVAR':
        case 'POPS':
        {
            argumentCountCheck(1, $normalizedLine);
            varCheck($normalizedLine[1]);
            addInstruction($instructionNum, $normalizedLine[0]);
            addArgument(1, "var", $normalizedLine[1]);
            endInstruction();
            break;
        }
        case 'CALL':
        case 'LABEL':
        case 'JUMP':
        {
            argumentCountCheck(1, $normalizedLine);
            labelCheck($normalizedLine[1]);
            addInstruction($instructionNum, $normalizedLine[0]);
            addArgument(1, "label", $normalizedLine[1]);
            endInstruction();
            break;
        }
        case 'PUSHS':
        case 'WRITE':
        case 'EXIT':
        {
            argumentCountCheck(1, $normalizedLine);
            symbolCheck($normalizedLine[1]);
            addInstruction($instructionNum, $normalizedLine[0]);
            addArgument(1, toVar(get_Type($normalizedLine[1])), getValue($normalizedLine[1]));
            endInstruction();
            break;
        }
        case 'MOVE':                //var symb
        case 'INT2CHAR':
        case 'STRLEN':
        case 'TYPE':
        {
            argumentCountCheck(2, $normalizedLine);
            varCheck($normalizedLine[1]);
            symbolCheck($normalizedLine[2]);
            addInstruction($instructionNum, $normalizedLine[0]);
            addArgument(1, "var", $normalizedLine[1]);
            addArgument(2, toVar(get_Type($normalizedLine[2])), getValue($normalizedLine[2]));
            endInstruction();
            break;
        }
        case 'READ':                //var type
        {
            argumentCountCheck(2, $normalizedLine);
            varCheck($normalizedLine[1]);
            typeCheck($normalizedLine[2]);
            addInstruction($instructionNum, $normalizedLine[0]);
            addArgument(1, "var", $normalizedLine[1]);
            addArgument(2, "type", $normalizedLine[2]);
            endInstruction();
            break;
        }
        case 'ADD':                 //var symb symb
        case 'SUB':
        case 'MUL':
        case 'IDIV':
        case 'LT':
        case 'GT':
        case 'EQ':
        case 'AND':
        case 'OR':
        case 'NOT':
        case 'STR2INT':
        case 'CONCAT':
        case 'GETCAHR':
        case 'SETCHAR':
        {
            argumentCountCheck(3, $normalizedLine);
            varCheck($normalizedLine[1]);
            symbolCheck($normalizedLine[2]);
            symbolCheck($normalizedLine[3]);
            addInstruction($instructionNum, $normalizedLine[0]);
            addArgument(1, "var", $normalizedLine[1]);
            addArgument(2, toVar(get_Type($normalizedLine[2])), getValue($normalizedLine[3]));
            addArgument(3, toVar(get_Type($normalizedLine[3])), getValue($normalizedLine[2]));
            endInstruction();
            break;
        }
        case 'JUMPIFEQ':
        case 'JUMPIFNEQ':
        {
            argumentCountCheck(3, $normalizedLine);
            labelCheck($normalizedLine[1]);
            symbolCheck($normalizedLine[2]);
            symbolCheck($normalizedLine[3]);
            addInstruction($instructionNum, $normalizedLine[0]);
            addArgument(1, "label", $normalizedLine[1]);
            addArgument(2, toVar(get_Type($normalizedLine[2])), getValue($normalizedLine[2]));
            addArgument(3, toVar(get_Type($normalizedLine[3])), getValue($normalizedLine[3]));
            endInstruction();
            break;
        }
        default:
        {
            fwrite(STDERR, "Spatne zapsana instrukce \n");
            exit(22);
        }

    }

    $instructionNum++;
}


$output.= "</program>\n";
//vypsani pozadovaneho nma stardni vystup
echo $output;


?>
