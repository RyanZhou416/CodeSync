; 脚本位置：CodeSync/build_scripts/win_setup.iss

; === 1. 接收命令行传来的参数 ===
#ifndef MyAppArch
  #define MyAppArch "x64"
#endif

#define MyAppName "代码同步 (CodeSync)"
#define MyAppVersion "1.0.3"
#define MyAppPublisher "Ryan"
#define MyAppExeName "CodeSync.exe"

[Setup]
AppId={{A3D8C9B0-1234-5678-ABCD-EFEFEFEFEFEF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultGroupName=CodeSync

; === 2. 架构设置 ===
#if MyAppArch == "x64"
  ArchitecturesAllowed=x64
  ArchitecturesInstallIn64BitMode=x64
#endif

DefaultDirName={autopf}\CodeSync

; === 3. 输出设置 ===
#ifndef MyOutputFilename
  #define MyOutputFilename "CodeSync_Setup"
#endif
OutputBaseFilename={#MyOutputFilename}
OutputDir=..\Output

Compression=lzma
SolidCompression=yes
SetupIconFile=..\assets\icon.ico

; === 4. 关键修复：让用户选择开始菜单 ===
; 允许用户在安装时选择“不创建开始菜单文件夹”
AllowNoIcons=yes
; 确保显示“选择开始菜单文件夹”的页面
DisableProgramGroupPage=no
; 确保显示“选择安装目录”的页面
DisableDirPage=no

; 卸载相关
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "chinesesimplified"; MessagesFile: "ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; 桌面快捷方式 (默认勾选)
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\lang.json"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
; === 5. 定义快捷方式 ===
; {group} 代表用户在安装界面选择的“开始菜单文件夹”
; 如果用户勾选了“不创建开始菜单文件夹”，这些图标将不会被创建
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; 桌面快捷方式 (关联到上面的 Tasks)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeUninstall(): Boolean;
var
  ErrorCode: Integer;
begin
  ShellExec('open', 'taskkill.exe', '/F /IM {#MyAppExeName} /T', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);
  Result := True;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
  begin
    if MsgBox('是否同时删除本地的配置文件和缓存数据？' #13#13 '这将删除所有保存的项目记录、主题和语言设置。', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{userappdata}\CodeSync'), True, True, True);
    end;
  end;
end;