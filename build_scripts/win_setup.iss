; 脚本位置：CodeSync/build_scripts/win_setup.iss

; === 1. 接收命令行参数 ===
#ifndef MyAppArch
  #define MyAppArch "x64"
#endif

#define MyAppName "代码同步 (CodeSync)"
#define MyAppVersion "1.0.7"
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

; === 4. 界面设置 ===
; 核心修改：隐藏原本的“选择开始菜单文件夹”页面
DisableProgramGroupPage=yes
; 仍然允许选择安装目录
DisableDirPage=no

; 卸载设置
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "chinesesimplified"; MessagesFile: "ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

; === 5. 任务 (附加任务页面) ===
[Tasks]
; 核心修改：在这里添加开始菜单的复选框
; Flags: checked 表示默认勾选
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startmenuicon"; Description: "创建开始菜单快捷方式"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\lang.json"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
; === 6. 图标定义 ===
; 核心修改：增加 Tasks: startmenuicon 限制
; 只有当用户勾选了上面的 startmenuicon 任务时，才会创建这些图标
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenuicon
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; Tasks: startmenuicon

; 桌面快捷方式
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