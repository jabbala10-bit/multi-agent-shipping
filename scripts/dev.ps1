param(
    [Parameter(Position = 0)]
    [string]$Command = "doctor",
    [Parameter(Position = 1)]
    [string]$Service = ""
)

$argsForPython = @("-m", "policymesh", $Command)
if ($Service -ne "") {
    $argsForPython += $Service
}

python @argsForPython
