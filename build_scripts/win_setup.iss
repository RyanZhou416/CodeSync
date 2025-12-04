; 脚本位置：CodeSync/build_scripts/win_setup.iss
; 编译前请先运行 win_build.bat 生成 exe

#define MyAppName "代码同步 (CodeSync)"
#define MyAppVersion "1.0"
#define MyAppPublisher "Ryan"
#define MyAppExeName "CodeSync.exe"

[Setup]
; NOTE: AppId 的值唯一标识该应用程序。
AppId={{A3D8C9B0-1234-5678-ABCD-EFEFEFEFEFEF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\CodeSync
DefaultGroupName=CodeSync
; 输出安装包的位置 (项目根目录/Output)
OutputDir=..\Output
#ifndef MyOutputFilename
  #define MyOutputFilename "CodeSync_Setup"
#endif

OutputBaseFilename={#MyOutputFilename}
Compression=lzma
SolidCompression=yes
; 图标设置 (如果你有 assets/icon.ico，取消下面注释)
; SetupIconFile=..\assets\icon.ico
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "chinesesimplified"; MessagesFile: "ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 1. 主程序 (从 dist 目录读取)
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; 2. 外部资源文件 (将 lang.json 复制到安装目录下的 assets 文件夹)
; 这样安装后，你可以直接去安装目录修改 json 来更新翻译
Source: "..\assets\lang.json"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

; === 卸载逻辑：强制关闭进程 + 询问删除配置 ===
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
      // 删除 %APPDATA%\CodeSync
      DelTree(ExpandConstant('{userappdata}\CodeSync'), True, True, True);
    end;
  end;
end;