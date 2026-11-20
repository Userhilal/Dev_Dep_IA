; Installateur non officiel TP6, autonome, pour la roue sentiment-app 1.0.1.
; Compatible Inno Setup 6.3+ ; cible Windows x64.
#define AppName "sentiment-app"
#define AppVersion "1.0.1"

[Setup]
AppId=sentiment-app.Userhilal.Dev_Dep_IA
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Projet sentiment-app
DefaultDirName={localappdata}\Programs\sentiment-app
DefaultGroupName=sentiment-app
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
OutputDir=Output
OutputBaseFilename=sentiment-app-{#AppVersion}-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ChangesEnvironment=yes
UninstallDisplayName=sentiment-app {#AppVersion}

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "addtopath"; Description: "Ajouter la commande sentiment au PATH utilisateur"; Flags: checkedonce

[Files]
Source: "build\app\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{userprograms}\sentiment-app\Analyser un avis"; Filename: "{cmd}"; Parameters: "/k """"{app}\sentiment.cmd"""""; WorkingDir: "{app}"
Name: "{userprograms}\sentiment-app\Desinstaller"; Filename: "{uninstallexe}"

[Code]
function StripUserPath(const Current, Item: String): String;
var
  Work, Needle: String;
  P: Integer;
begin
  Work := ';' + Current + ';';
  Needle := ';' + Item + ';';
  P := Pos(Lowercase(Needle), Lowercase(Work));
  while P > 0 do
  begin
    Delete(Work, P, Length(Needle) - 1);
    P := Pos(Lowercase(Needle), Lowercase(Work));
  end;
  if Length(Work) <= 2 then
    Result := ''
  else
    Result := Copy(Work, 2, Length(Work) - 2);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Existing, Folder: String;
begin
  if (CurStep <> ssPostInstall) or (not WizardIsTaskSelected('addtopath')) then
    exit;
  Folder := ExpandConstant('{app}');
  if not RegQueryStringValue(HKCU, 'Environment', 'Path', Existing) then
    Existing := '';
  Existing := StripUserPath(Existing, Folder);
  if Existing <> '' then
    Existing := Existing + ';';
  if not RegWriteExpandStringValue(HKCU, 'Environment', 'Path', Existing + Folder) then
    MsgBox('Impossible de mettre a jour le PATH utilisateur.', mbError, MB_OK);
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Existing, Updated: String;
begin
  if CurUninstallStep <> usPostUninstall then exit;
  if not RegQueryStringValue(HKCU, 'Environment', 'Path', Existing) then exit;
  Updated := StripUserPath(Existing, ExpandConstant('{app}'));
  if Updated <> Existing then
    RegWriteExpandStringValue(HKCU, 'Environment', 'Path', Updated);
end;
