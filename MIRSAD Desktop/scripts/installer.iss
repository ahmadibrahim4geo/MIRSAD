; One per-user installation. User projects are never part of the uninstall list.
#ifndef SourceDir
  #error SourceDir must name the verified application bundle
#endif
#ifndef OutputDir
  #error OutputDir is required
#endif
#ifndef ProductVersion
  #define ProductVersion "0.4.0.dev1"
#endif

[Setup]
AppId={code:ApplicationIdentity}
AppName=MIRSAD Desktop
AppVersion={#ProductVersion}
AppPublisher=Ahmad Ibrahim
AppPublisherURL=https://github.com/ahmadibrahim4geo/MIRSAD
AppSupportURL=https://github.com/ahmadibrahim4geo/MIRSAD/issues
DefaultDirName={localappdata}\Programs\MIRSAD
DefaultGroupName=MIRSAD
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.19041
WizardStyle=modern
DisableProgramGroupPage=yes
AllowNoIcons=yes
UsePreviousAppDir=yes
UsePreviousLanguage=no
OutputDir={#OutputDir}
OutputBaseFilename=MIRSAD-Setup
SetupIconFile={#SourceDir}\_internal\assets\mirsad.ico
UninstallDisplayIcon={app}\MIRSAD.exe
Compression=lzma2/fast
SolidCompression=yes
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
VersionInfoCompany=Ahmad Ibrahim
VersionInfoDescription=MIRSAD Desktop Installer
VersionInfoVersion=0.4.0.1

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\MIRSAD Desktop"; Filename: "{app}\MIRSAD.exe"; WorkingDir: "{userdocs}"
Name: "{autodesktop}\MIRSAD Desktop"; Filename: "{app}\MIRSAD.exe"; Tasks: desktopicon; WorkingDir: "{userdocs}"

[Run]
Filename: "{app}\MIRSAD.exe"; Description: "Open MIRSAD Desktop"; Flags: nowait postinstall skipifsilent unchecked

[Code]
function ApplicationIdentity(Param: String): String;
begin
  if ExpandConstant('{param:QA|0}') = '1' then
    Result := 'MIRSAD.Desktop.InstallationQA'
  else
    Result := 'MIRSAD.Desktop';
end;
