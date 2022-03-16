<?php
ini_set('dispalay_errors', 'stderr');


$header = False;

$instructionNum = 1;

$variable = True;


$output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
$output.= "<program language=\"IPPcode22\">\n";



Function removeComment (string $comLine)
{
    if (strpos($comLine, '#') != NULL)
    {
        return substr($comLine, 0, strpos($comLine, '#'));
    }
    return $comLine;
}


Function addInstruction (int $order, string $opcode)
{
    global $output;
    $output.= "<instruction order=\"";
    $output.= $order;
    $output.= "\" opcode=\"";
    $output.= $opcode;
    $output.= "\">\n";
}

Function endInstruction()
{
    global $output;
    $output.= "</instruction>\n";
}

Function addArgument(int $argNum, string $argType, string $argData)
{
    global $output;
    $output.= "<arg".$argNum." type=\"".$argType."\">".$argData."</arg".$argNum.">\n";
}

Function argumentCountCheck(int $num, array $data)
{
    if($num != count($data) - 1)
    {
        fwrite(STDERR, "Spatny pocet argumentu intrukce \n");
        exit(23);
    }
}

Function varCheck(string $var)
{
    if (!preg_match("/^(LF|TF|GF)@[a-zA-Z_$&%*!?-][a-zA-Z0-9_$&%*!?-]*$/", $var))
    {
        fwrite(STDERR, "Spatne zapsana promenna \n");
        exit(23);
    }
}

Function labelCheck(string $label)
{
    if (!preg_match("/^[a-zA-Z_$&%*!?-][a-zA-Z0-9_$&%*!?-]*$/", $label))
    {
        fwrite(STDERR, "Spatne zapsane navesti \n");
        exit(23);
    }

}

Function symbolCheck(string $symbol)
{
    if (!(preg_match("/^(GF|LF|TF|bool|nil)@[a-zA-Z_$&%*!?-][\S]*/", $symbol) || preg_match("/^string@[\S]*$/", $symbol) ||preg_match("/^int@[+-]{0,1}[\d]{1,}$/", $symbol)))
    {
        fwrite(STDERR, "Spatne zapsany symbol \n");
        exit(23);
    }
}

Function typeCheck(string $type)
{
    if (!($type == "int" || $type == "string" || $type == "bool"))
    {
    fwrite(STDERR, "Spatne zapsany symbol \n");
        exit(23);
    }
}

Function get_Type(string $symbol)
{
    if (strpos($symbol, '@') != NULL)
    {
        return substr($symbol, 0, strpos($symbol, '@'));
    }
    return $symbol;
}

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




while($line = fgets(STDIN))
{
    if ($line == "\n" || $line[0] == '#')
    {
        continue;
    }


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

    $normalizedLine = explode(' ', rtrim(removeComment(trim(ltrim($line)), "\n")));

    switch(strtoupper($normalizedLine[0]))
    {

        case 'CREATEFRAME':
        case 'PUSHFRAME':
        case 'POPFRAME':
        case 'RETURN':
        case 'BREAK':
        {
            argumentCountCheck(0, $normalizedLine);
            addInstruciont($instructionNum, $normalizedLine[0]);
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

echo $output;


?>
