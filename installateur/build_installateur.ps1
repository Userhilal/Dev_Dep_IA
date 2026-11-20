# Construction locale d'un installateur Windows autonome depuis la roue TP4 v1.0.1.
# A executer dans l'environnement virtuel Python 3.11.9 qui a construit la roue.
[CmdletBinding()]
param(
    [string]$Roue = 'dist\sentiment_app-1.0.1-py3-none-any.whl',
    [string]$PythonVersion = '3.11.9',
    [switch]$SansCompilation
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = (Resolve-Path (Join-Path $scriptDir '..')).Path
$build = Join-Path $scriptDir 'build'
$app = Join-Path $build 'app'
$embedded = Join-Path $app 'python'
$site = Join-Path $embedded 'Lib\site-packages'
$wheelhouse = Join-Path $build 'wheelhouse'
$constraints = Join-Path $build 'versions-python.txt'
$python = (Get-Command python -ErrorAction Stop).Source

function Check-Exit([string]$label) {
    if ($LASTEXITCODE -ne 0) { throw "$label a echoue (code $LASTEXITCODE)." }
}

if (-not [Environment]::Is64BitOperatingSystem) { throw 'Windows 64 bits est requis.' }
if (-not [Environment]::Is64BitProcess) { throw 'Ouvrez PowerShell 64 bits.' }
$active = (& $python -c 'import platform; print(platform.python_version())').Trim()
Check-Exit 'Detection de Python'
if ($active -ne $PythonVersion) {
    throw "Python actif : $active ; Python embarque demande : $PythonVersion. Activez le venv Python $PythonVersion pour respecter le modele."
}
if ($PythonVersion -ne '3.11.9') {
    throw 'Cette version du kit est testable uniquement avec Python embarque 3.11.9 / Windows x64.'
}

if ([IO.Path]::IsPathRooted($Roue)) { $wheelCandidate = $Roue }
else { $wheelCandidate = Join-Path $root $Roue }
if (-not (Test-Path -LiteralPath $wheelCandidate -PathType Leaf)) {
    throw "Roue absente : $wheelCandidate. Ne reconstruisez pas sans avoir copie le modele dans la roue."
}
$wheel = (Resolve-Path -LiteralPath $wheelCandidate).Path
if ((Split-Path $wheel -Leaf) -ne 'sentiment_app-1.0.1-py3-none-any.whl') {
    throw "La roue attendue est sentiment_app-1.0.1-py3-none-any.whl, trouve : $wheel"
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($wheel)
try {
    $model = $zip.GetEntry('sentiment_app/modele/sentiment.joblib')
    if (($null -eq $model) -or $model.Length -lt 1000) {
        throw 'La roue ne contient pas un modele sentiment.joblib valide : ne pas generer de setup.'
    }
} finally { $zip.Dispose() }
Write-Host "OK roue : $wheel"
Write-Host "OK modele present dans la roue"
Write-Host "OK Python actif : $active"

$iscc = $null
$command = Get-Command 'ISCC.exe' -ErrorAction SilentlyContinue
if ($command) { $iscc = $command.Source }
if (-not $iscc) {
    $programs = @($env:ProgramFiles, [Environment]::GetEnvironmentVariable('ProgramFiles(x86)'), $env:LOCALAPPDATA)
    foreach ($base in $programs) {
        if ([string]::IsNullOrWhiteSpace($base)) { continue }
        foreach ($folder in @('Inno Setup 6', 'Inno Setup 7', 'Programs\Inno Setup 6', 'Programs\Inno Setup 7')) {
            $candidate = Join-Path $base "$folder\ISCC.exe"
            if (Test-Path -LiteralPath $candidate) { $iscc = $candidate; break }
        }
        if ($iscc) { break }
    }
}
if ((-not $SansCompilation) -and (-not $iscc)) {
    throw 'ISCC.exe absent. Installez Inno Setup via : winget install --id JRSoftware.InnoSetup --exact'
}

if (Test-Path -LiteralPath $build) { Remove-Item -LiteralPath $build -Recurse -Force }
New-Item -ItemType Directory -Force -Path $embedded, $site, $wheelhouse | Out-Null

# Pins de toutes les dependances deja installees, pour une compatibilite maximale.
$freezelines = & $python -m pip list --format=freeze
Check-Exit 'Releve des versions du venv'
$freezelines | Where-Object { $_ -match '^[A-Za-z0-9_.-]+==[A-Za-z0-9_.+!~-]+$' } |
    Set-Content -LiteralPath $constraints -Encoding Ascii
Write-Host "OK versions relevees dans $constraints"

$embedZip = Join-Path $build "python-$PythonVersion-embeddable-amd64.zip"
$url = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embeddable-amd64.zip"
Write-Host "Telechargement du Python embarque officiel : $url"
Invoke-WebRequest -Uri $url -OutFile $embedZip -UseBasicParsing
Expand-Archive -LiteralPath $embedZip -DestinationPath $embedded -Force
$pth = Join-Path $embedded 'python311._pth'
if (-not (Test-Path $pth)) { throw 'Fichier python311._pth absent dans le Python embarque.' }
@('python311.zip', '.', 'Lib\site-packages', 'import site') |
    Set-Content -LiteralPath $pth -Encoding Ascii
Write-Host 'OK python311._pth configure.'

Write-Host 'Recuperation de roues Windows x64 CPython 3.11 et versions contraintes ...'
& $python -m pip download --disable-pip-version-check --only-binary=:all: `
    --platform win_amd64 --python-version 3.11 --implementation cp --abi cp311 `
    --constraint $constraints --dest $wheelhouse $wheel
Check-Exit 'Telechargement des dependances Windows'

Write-Host 'Installation des roues en local dans le Python embarque ...'
& $python -m pip install --disable-pip-version-check --no-index `
    --find-links $wheelhouse --target $site --no-compile --ignore-installed `
    --constraint $constraints $wheel
Check-Exit 'Installation des dependances dans build/app'

Copy-Item -LiteralPath (Join-Path $scriptDir 'sentiment.cmd') -Destination (Join-Path $app 'sentiment.cmd')
Copy-Item -LiteralPath (Join-Path $scriptDir 'LISEZMOI.txt') -Destination (Join-Path $app 'LISEZMOI.txt')
$launcher = Join-Path $app 'sentiment.cmd'

Write-Host 'Tests de la distribution autonome sans activer de venv ...'
$versionText = (& $launcher --version | Out-String).Trim()
Check-Exit 'Test --version'
if ($versionText -ne 'sentiment-app 1.0.1') { throw "Version inattendue : $versionText" }
Write-Host "OK $versionText"
$resultJson = (& $launcher --json 'Produit casse et service injoignable' | Out-String).Trim()
Check-Exit 'Test de prediction JSON'
$prediction = $resultJson | ConvertFrom-Json
if (($prediction.label -notin @('positive','negative')) -or ($prediction.score -lt 0) -or ($prediction.score -gt 1)) {
    throw "Prediction JSON invalide : $resultJson"
}
Write-Host "OK prediction : $resultJson"
# Ne pas imbriquer de guillemets Python dans -c : Windows PowerShell 5.1 les retire.
# La prediction reelle a deja ete verifiee par sentiment.cmd --json juste au-dessus.
$importCheck = (& (Join-Path $embedded 'python.exe') -c 'from sentiment_app import predict; print(callable(predict))' | Out-String).Trim()
Check-Exit 'Test import Python dans le Python embarque'
if ($importCheck -ne 'True') { throw "Import predict invalide : $importCheck" }
Write-Host "OK import Python : $importCheck"

if ($SansCompilation) {
    Write-Host "OK tests autonomes. Dossier prepare : $app"
    Write-Host 'Option -SansCompilation : aucun setup.exe genere.'
    exit 0
}

Write-Host 'Compilation Inno Setup ...'
& $iscc (Join-Path $scriptDir 'sentiment.iss')
Check-Exit 'Compilation ISCC'
$setup = Join-Path $scriptDir 'Output\sentiment-app-1.0.1-setup.exe'
if (-not (Test-Path $setup)) { throw "ISCC a termine mais le fichier manque : $setup" }
Get-Item $setup | Select-Object FullName, Length
Get-FileHash -Algorithm SHA256 $setup | Format-List
Write-Host 'Termine. Tester ensuite setup.exe sur un compte Windows vierge ou une Sandbox.'
