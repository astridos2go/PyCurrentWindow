; Script generated by the Inno Script Studio Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "PyCurrentWindow"
#define MyAppVersion "v1.1"
#define MyAppPublisher "David Blum"
#define MyAppExeName "PyCurrentWindow.exe"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
OutputBaseFilename=PyCurrentWindow Installer ({#MyAppVersion})
OutputDir=.\installer
PrivilegesRequired=none
LicenseFile={#SourcePath}\LICENSE
WizardStyle=modern
DefaultDirName={code:getDirName}
AppCopyright=David Blum
AppId={{860F4F89-FC86-42CF-A5C3-5E9AA7D7E84C}
SetupIconFile={#SourcePath}\executable\images\icon.ico
UninstallDisplayIcon={uninstallexe}
SolidCompression=True

[Files]
Source: "executable\*"; DestDir: "{app}"; Flags: ignoreversion createallsubdirs recursesubdirs

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[InstallDelete]
Type: filesandordirs; Name: "{app}"

[Registry]
Root: "HKCU"; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "PyCurrentWindow"; ValueData: """{app}\PyCurrentWindow.exe"""; Flags: uninsdeletevalue; Tasks: run_on_login

[Tasks]
Name: "run_on_login"; Description: "{cm:AutoStartProgram,PyCurrentWindow}"; GroupDescription: "{cm:AutoStartProgramGroupDescription}"

[Code]
function GetDirName(Param: string): string;
begin
  if IsAdminInstallMode then
    Result := ExpandConstant('{pf}\{#MyAppName}')
  else
    Result := ExpandConstant('{localappdata}\{#MyAppName}');
end;