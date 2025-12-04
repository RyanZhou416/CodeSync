; 脚本位置：CodeSync/build_scripts/win_setup.iss

; === 1. 接收命令行传来的参数 ===
; 默认值设为 x64，方便本地测试。在 GitHub Actions 中会被覆盖。
#ifndef MyAppArch
  #define MyAppArch "x64"
#endif

#define MyAppName "代码同步 (CodeSync)"
#define MyAppVersion "1.0.2"
#define MyAppPublisher "Ryan"
#define MyAppExeName "CodeSync.exe"

[Setup]
AppId={{A3D8C9B0-1234-5678-ABCD-EFEFEFEFEFEF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultGroupName=CodeSync

; === 2. 核心修复：根据架构动态调整安装目录 ===
; 如果传入的是 x64，开启 64 位安装模式
#if MyAppArch == "x64"
  ArchitecturesAllowed=x64
  ArchitecturesInstallIn64BitMode=x64
  ; 在 64 位模式下，{autopf} 会自动指向 C:\Program Files
#endif

DefaultDirName={autopf}\CodeSync

; === 3. 输出文件名设置 ===
#ifndef MyOutputFilename
  #define MyOutputFilename "CodeSync_Setup"
#endif
OutputBaseFilename={#MyOutputFilename}
OutputDir=..\Output

Compression=lzma
SolidCompression=yes
; 图标 (确保 assets 文件夹里有 icon.ico)
SetupIconFile=..\assets\icon.ico

; === 4. 界面设置 ===
; 允许用户在安装过程中更改设置
DisableProgramGroupPage=no
DisableDirPage=no
; 卸载相关
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "chinesesimplified"; MessagesFile: "ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

; === 5. 任务 (勾选框) ===
; 这里定义安装向导中的“附加任务”页面
[Tasks]
; 创建桌面快捷方式 (Flags: unchecked 表示默认不勾选，checked 表示默认勾选)
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checked
; 创建开始菜单文件夹
; Inno Setup 默认会创建开始菜单文件夹，除非在这里或者 [Setup] 禁止。
; 但如果我们要一个额外的“快速启动栏”或者其他，可以在这里加。
; 通常开始菜单入口由 [Icons] 控制，不需要在这里作为一个 Task，除非你想让用户选择“是否创建”。

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\lang.json"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
; 主菜单快捷方式 (始终创建)
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; 卸载程序快捷方式
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; 桌面快捷方式 (仅当用户勾选了 desktopicon 任务时创建)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
// 保持之前的卸载逻辑不变
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