
if ($args.Count -lt 2){
    Write-Host "bindiff.ps1 primiary secondary"
    exit
}
$primiary_file=$args[0].Split("/")[-1]
$secondary_file=$args[1].Split("/")[-1]
Write-Host -NoNewline "The primiary file is "
Write-Host -ForegroundColor red $primiary_file
Write-Host -NoNewline "The secondary file is "
Write-Host -ForegroundColor red $secondary_file
if (-not (Test-Path  $primiary_file".i64")){
    Write-Host -NoNewline "Generating "
    Write-Host -ForegroundColor red $primiary_file".i64"
    idat64.exe -B $primiary_file;
    Remove-Item $primiary_file".asm"
}
if (-not (Test-Path  $secondary_file".i64")){
    Write-Host -NoNewline "Generating "
    Write-Host -ForegroundColor red $secondary_file".i64"
    idat64.exe -B $secondary_file;
    Remove-Item $secondary_file".asm"
}
if (-not (Test-Path  $primiary_file".BinExport")){
    Write-Host -NoNewline "Generating "
    Write-Host -ForegroundColor red $primiary_file".BinExport"
    idat64.exe  -A -OBinExportAutoAction:BinExportBinary  -OBinExportModule:$primiary_file".BinExport" $primiary_file
}

if (-not (Test-Path  $secondary_file".BinExport")){
    Write-Host -NoNewline "Generating "
    Write-Host -ForegroundColor red $secondary_file".BinExport"
    idat64.exe  -A -OBinExportAutoAction:BinExportBinary  -OBinExportModule:$secondary_file".BinExport" $secondary_file
}
if (-not (Test-Path  $primiary_file"_vs_"$secondary_file".BinDiff")){
    Write-Host -NoNewline "Generating "
    Write-Host -ForegroundColor red $primiary_file"_vs_"$secondary_file".BinDiff"
    bindiff.exe  --primary $primiary_file".BinExport" --secondary $secondary_file".BinExport"
}
Write-Host -NoNewline "Final result is "
Write-Host -ForegroundColor red $primiary_file"_vs_"$secondary_file".BinDiff";
