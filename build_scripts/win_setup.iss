; 脚本位置：CodeSync/build_scripts/win_setup.iss

; =================================================================
; 1. 预处理器：动态读取版本号和架构
; =================================================================
; --- 读取根目录的 VERSION 文件 ---
#define FileHandle
#define FileLine
#if FileHandle = FileOpen("..\VERSION")
  #define FileLine = FileRead(FileHandle)
  #expr FileClose(FileHandle)
#endif

; 如果读取失败，默认 1.0.0
#ifdef FileLine
  #define MyAppVersion FileLine
#else
  #define MyAppVersion "1.0.0"
#endif

; --- 接收命令行参数 (架构) ---
#ifndef MyAppArch
  #define MyAppArch "x64"
#endif

#define MyAppName "代码同步 (CodeSync)"
#define MyAppPublisher "Ryan"
#define MyAppExeName "CodeSync.exe"
; === 新增：定义图标文件路径 ===
#define MyAppIcon "..\assets\icon.ico"


; =================================================================
; 2. 安装程序核心设置
; =================================================================
[Setup]
AppId={{A3D8C9B0-1234-5678-ABCD-EFEFEFEFEFEF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultGroupName=CodeSync

; --- 架构适配 ---
#if MyAppArch == "x64"
  ArchitecturesAllowed=x64
  ArchitecturesInstallIn64BitMode=x64
#endif

; 默认安装目录
DefaultDirName={autopf}\CodeSync

; --- 输出设置 ---
OutputBaseFilename=CodeSync_Setup_v{#MyAppVersion}_{#MyAppArch}
OutputDir=..\Output

Compression=lzma
SolidCompression=yes
; 确保安装程序EXE本身的图标是正确的
SetupIconFile={#MyAppIcon}

; --- 界面与逻辑 ---
DisableProgramGroupPage=yes
DisableDirPage=no
; 确保卸载程序有图标
UninstallDisplayIcon={#MyAppIcon}
; 卸载相关
CloseApplications=yes
RestartApplications=no

; =================================================================
; 3. 多语言支持
; =================================================================
[Languages]
Name: "chinesesimplified"; MessagesFile: "ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

; === 自定义翻译 (解决硬编码英文问题) ===
[CustomMessages]
english.AdditionalIcons=Additional shortcuts
chinesesimplified.AdditionalIcons=附加快捷方式

english.CreateDesktopIcon=Create a desktop shortcut
chinesesimplified.CreateDesktopIcon=创建桌面快捷方式

english.CreateStartMenuIcon=Create a Start Menu shortcut
chinesesimplified.CreateStartMenuIcon=创建开始菜单快捷方式

; =================================================================
; 4. 任务列表 (附加任务页面)
; =================================================================
[Tasks]
; 桌面快捷方式
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

; 开始菜单快捷方式 (新增)
Name: "startmenuicon"; Description: "{cm:CreateStartMenuIcon}"; GroupDescription: "{cm:AdditionalIcons}"

; =================================================================
; 5. 文件打包
; =================================================================
[Files]
; 主程序
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; 语言包 & 版本文件
Source: "..\assets\lang.json"; DestDir: "{app}\assets"; Flags: ignoreversion
; === 确保图标文件也被打包进去 (因为快捷方式要引用它) ===
Source: "{#MyAppIcon}"; DestDir: "{app}\assets"; Flags: ignoreversion


; =================================================================
; 6. 快捷方式生成
; =================================================================
[Icons]
; 开始菜单快捷方式 (主程序) - IconFilename 指向安装后的图标文件
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenuicon; IconFilename: "{app}\assets\icon.ico"
; 开始菜单快捷方式 (卸载程序)
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; Tasks: startmenuicon; IconFilename: "{app}\assets\icon.ico"

; 桌面图标
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\assets\icon.ico"

; =================================================================
; 7. 运行
; =================================================================
[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

; =================================================================
; 8. Pascal 脚本 (卸载逻辑)
; =================================================================
[Code]
// 1. 初始化卸载：强制关闭正在运行的软件
function InitializeUninstall(): Boolean;
var
  ErrorCode: Integer;
begin
  // 运行 taskkill 命令强制结束 CodeSync.exe 进程
  ShellExec('open', 'taskkill.exe', '/F /IM {#MyAppExeName} /T', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);
  Result := True;
end;

// 2. 卸载步骤变更：询问是否删除配置文件
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
  begin
    if MsgBox('是否同时删除本地的配置文件和缓存数据？' #13#13 '这将删除所有保存的项目记录、主题和语言设置。', mbConfirmation, MB_YESNO) = IDYES then
    begin
      // 删除 %APPDATA%\CodeSync 文件夹
      DelTree(ExpandConstant('{userappdata}\CodeSync'), True, True, True);
    end;
  end;
end;