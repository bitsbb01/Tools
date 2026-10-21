#define AppName "JGJG Video Studio"
#define AppVersion "0.1.0"
#define AppPublisher "JGJG Books"
#define AppExeName "JGJG Video Studio.exe"

[Setup]
AppId={{8A2763C3-4BCC-48ED-A8A5-53473CF5B86E}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\JGJG Books\JGJG Video Studio
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
OutputDir=..\dist\installer
OutputBaseFilename=JGJG-Video-Studio-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#AppExeName}
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64
LicenseFile=..\third-party\FFmpeg-COPYING.LGPLv2.1.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "..\dist\JGJG Video Studio.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\third-party\FFmpeg-COPYING.LGPLv2.1.txt"; DestDir: "{app}\licenses"; Flags: ignoreversion
Source: "..\THIRD-PARTY-NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: postinstall nowait skipifsilent
