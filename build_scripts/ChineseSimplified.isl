; *** Inno Setup version 6.0.0+ Chinese Simplified messages ***
;
[LangOptions]
LanguageName=Chinese Simplified
LanguageID=$0804
LanguageCodePage=936
; If the language is not displayed correctly in the installer, try changing the
; following font settings.
DialogFontName=宋体
DialogFontSize=9
WelcomeFontName=宋体
WelcomeFontSize=12
TitleFontName=宋体
TitleFontSize=29
CopyrightFontName=Arial
CopyrightFontSize=8

[Messages]

; *** Application titles
SetupAppTitle=安装
SetupWindowTitle=安装 - %1
UninstallAppTitle=卸载
UninstallAppFullTitle=%1 卸载

; *** Misc. common
InformationTitle=信息
ConfirmTitle=确认
ErrorTitle=错误

; *** SetupLdr messages
SetupLdrStartupMessage=这将安装 %1。是否继续？
LdrCannotCreateTemp=不能创建临时文件。安装中止
LdrCannotExecTemp=不能在临时目录中执行文件。安装中止

; *** Startup error messages
LastErrorMessage=%1.%n%n错误 %2: %3
SetupFileMissing=在安装目录中找不到文件 %1。请更正这个问题或获取一个新的文件副本。
SetupFileCorrupt=文件已损坏。请获取一个新的文件副本。
SetupFileCorruptOrWrongVer=文件已损坏，或是与这个版本的安装程序不兼容。请更正这个问题或获取一个新的文件副本。
InvalidParameter=无效的命令行参数: %n%n%1
SetupAlreadyRunning=安装程序正在运行。
WindowsVersionNotSupported=这个程序不支持你的计算机运行的 Windows 版本。
WindowsServicePackRequired=这个程序要求 %1 Service Pack %2 或更高。
NotOnThisPlatform=这个程序将不能在 %1 上运行。
OnlyOnThisPlatform=这个程序必须在 %1 上运行。
OnlyOnTheseArchitectures=这个程序只能在以下处理器架构的 Windows 版本中安装:%n%n%1
WinVersionTooLowError=这个程序要求 %1 版本 %2 或更高。
WinVersionTooHighError=这个程序不能在 %1 版本 %2 或更高版本中安装。
AdminPrivilegesRequired=在安装这个程序时你需要以管理员身份登录。
PowerUserPrivilegesRequired=在安装这个程序时你需要以管理员身份或有权限的用户身份登录。
SetupAppRunningError=安装程序检测到 %1 当前正在运行。%n%n请现在关闭它的所有实例，然后单击“确定”继续，或“取消”退出。
UninstallAppRunningError=卸载程序检测到 %1 当前正在运行。%n%n请现在关闭它的所有实例，然后单击“确定”继续，或“取消”退出。

; *** Startup questions
PrivilegesRequiredOverrideTitle=选择安装模式
PrivilegesRequiredOverrideInstruction=选择安装模式
PrivilegesRequiredOverrideText1=%1 可以为所有用户安装 (需要管理员权限)，或仅为你安装。
PrivilegesRequiredOverrideText2=%1 只能为你安装，或为所有用户安装 (需要管理员权限)。
PrivilegesRequiredOverrideAllUsers=为所有用户安装(&A)
PrivilegesRequiredOverrideAllUsersRecommended=为所有用户安装 (&A) (推荐)
PrivilegesRequiredOverrideCurrentUser=仅为我安装(&M)
PrivilegesRequiredOverrideCurrentUserRecommended=仅为我安装 (&M) (推荐)

; *** Misc. errors
ErrorCreatingDir=安装程序不能创建目录 "%1"
ErrorTooManyFilesInDir=不能在目录 "%1" 中创建文件，因为里面的文件太多

; *** Setup common messages
ExitSetupTitle=退出安装
ExitSetupMessage=安装未完成。如果你现在退出，程序将不会被安装。%n%n你可以以后再运行安装程序完成安装。%n%n退出安装吗？
AboutSetupMenuItem=关于安装程序(&A)...
AboutSetupTitle=关于安装程序
AboutSetupMessage=%1 版本 %2%n%3%n%n%1 主页:%n%4
AboutSetupNote=
TranslatorNote=

; *** Buttons
ButtonBack=< 上一步(&B)
ButtonNext=下一步(&N) >
ButtonInstall=安装(&I)
ButtonOK=确定
ButtonCancel=取消
ButtonYes=是(&Y)
ButtonYesToAll=全是(&A)
ButtonNo=否(&N)
ButtonNoToAll=全否(&O)
ButtonFinish=完成(&F)
ButtonBrowse=浏览(&B)...
ButtonWizardBrowse=浏览(&R)...
ButtonNewFolder=新建文件夹(&M)

; *** "Select Language" dialog messages
SelectLanguageTitle=选择安装语言
SelectLanguageLabel=选择安装时要使用的语言。

; *** Common wizard text
ClickNext=单击“下一步”继续，或单击“取消”退出安装程序。
BeveledLabel=
BrowseDialogTitle=浏览文件夹
BrowseDialogLabel=在下面的列表中选择一个文件夹，然后单击“确定”。
NewFolderName=新文件夹

; *** "Welcome" wizard page
WelcomeLabel1=欢迎使用 [name] 安装向导
WelcomeLabel2=这个向导将指引你完成 [name/ver] 的安装。%n%n在开始安装之前，建议先关闭其他所有应用程序。这将允许“安装程序”更新指定的系统文件，而不需要重新启动你的计算机。


; *** "Password" wizard page
WizardPassword=密码
PasswordLabel1=这个安装程序受密码保护。
PasswordLabel3=请输入密码，密码区分大小写。然后单击“下一步”继续。
PasswordEditLabel=密码(&P):
IncorrectPassword=你输入的密码不正确，请重试。

; *** "License Agreement" wizard page
WizardLicense=许可协议
LicenseLabel1=在继续安装之前，请阅读下列重要信息。
LicenseLabel3=请阅读下列许可协议。在继续安装之前，你必须接受此协议的条款。
LicenseAccepted=我接受协议(&A)
LicenseNotAccepted=我不接受协议(&I)

; *** "Information" wizard pages
WizardInfoBefore=信息
InfoBeforeLabel=在继续安装之前，请阅读下列重要信息。
InfoBeforeClickLabel=准备好继续安装后，单击“下一步”。
WizardInfoAfter=信息
InfoAfterLabel=在继续安装之前，请阅读下列重要信息。
InfoAfterClickLabel=准备好继续安装后，单击“下一步”。

; *** "User Information" wizard page
WizardUserInfo=用户信息
UserInfoDesc=请输入你的信息。
UserInfoName=用户名(&U):
UserInfoOrg=组织(&O):
UserInfoSerial=序列号(&S):
UserInfoNameRequired=你必须输入一个名称。

; *** "Select Destination Location" wizard page
WizardSelectDir=选择目标位置
SelectDirDesc=你将把 [name] 安装在哪里？
SelectDirLabel3=安装程序将把 [name] 安装在下列文件夹中。
SelectDirBrowseLabel=若要继续，单击“下一步”。如果你想选择其它文件夹，单击“浏览”。
DiskSpaceMBLabel=至少需要有 [mb] MB 的可用磁盘空间。
CannotInstallToNetworkDrive=安装程序无法安装到一个网络驱动器。
CannotInstallToUNCPath=安装程序无法安装到一个 UNC 路径。
InvalidPath=你必须输入一个包含盘符的完整路径；例如:%n%nC:\APP%n%n或一个网络路径，例如:%n%n\\server\share
InvalidDrive=你选定的驱动器或 UNC 共享不存在或不能访问。请另外选择。
DiskSpaceWarningTitle=没有足够的磁盘空间
DiskSpaceWarning=安装程序至少需要 %1 KB 的可用磁盘空间才能安装，但选定的驱动器只有 %2 KB 的可用空间。%n%n你一定要继续吗？
DirNameTooLong=文件夹名称或路径太长。
InvalidDirName=文件夹名称无效。
BadDirName32=文件夹名称不能包含下列任何字符:%n%n%1
DirExistsTitle=文件夹已存在
DirExists=文件夹:%n%n%1%n%n已经存在。你一定要安装到那个文件夹吗？
DirDoesntExistTitle=文件夹不存在
DirDoesntExist=文件夹:%n%n%1%n%n不存在。你想创建它吗？

; *** "Select Components" wizard page
WizardSelectComponents=选择组件
SelectComponentsDesc=你想安装哪些组件？
SelectComponentsLabel2=选择你想要安装的组件；清除你不想安装的组件。然后单击“下一步”继续。
FullInstallation=完全安装
; if possible don't translate 'Compact' as 'Minimal' (I mean 'Minimal' in your language)
CompactInstallation=简洁安装
CustomInstallation=自定义安装
NoUninstallWarningTitle=组件存在
NoUninstallWarning=安装程序检测到下列组件已在你的计算机中安装:%n%n%1%n%n取消选择这些组件将不会卸载它们。%n%n你一定要继续吗？
ComponentSize1=%1 KB
ComponentSize2=%1 MB
ComponentsDiskSpaceMBLabel=当前选择至少需要 [mb] MB 的可用磁盘空间。

; *** "Select Additional Tasks" wizard page
WizardSelectTasks=选择附加任务
SelectTasksDesc=你想执行哪些附加任务？
SelectTasksLabel2=选择在安装 [name] 时要执行的附加任务，然后单击“下一步”。

; *** "Select Start Menu Folder" wizard page
WizardSelectProgramGroup=选择开始菜单文件夹
SelectStartMenuFolderDesc=安装程序应该在哪里放置程序的快捷方式？
SelectStartMenuFolderLabel3=安装程序将在下列“开始”菜单文件夹中创建程序的快捷方式。
SelectStartMenuFolderBrowseLabel=若要继续，单击“下一步”。如果你想选择其它文件夹，单击“浏览”。
MustEnterGroupName=你必须输入一个文件夹名称。
GroupNameTooLong=文件夹名称或路径太长。
InvalidGroupName=文件夹名称无效。
BadGroupName=文件夹名称不能包含下列任何字符:%n%n%1
NoProgramGroupCheck2=不创建“开始”菜单文件夹(&D)

; *** "Ready to Install" wizard page
WizardReady=准备安装
ReadyLabel1=安装程序现在准备开始安装 [name] 到你的计算机。
ReadyLabel2a=单击“安装”继续此安装程序。如果你想回顾或改变设置，请单击“上一步”。
ReadyLabel2b=单击“安装”继续此安装程序？如果你想回顾或改变设置，请单击“上一步”。
ReadyMemoUserInfo=用户信息:
ReadyMemoDir=目标位置:
ReadyMemoType=安装类型:
ReadyMemoComponents=选定组件:
ReadyMemoGroup=“开始”菜单文件夹:
ReadyMemoTasks=附加任务:

; *** "Preparing to Install" wizard page
WizardPreparing=正在准备安装
PreparingDesc=安装程序正在准备安装 [name] 到你的计算机。
PreviousInstallNotCompleted=先前的程序安装/卸载未完成。你需要重新启动你的计算机才能完成安装。%n%n在重新启动计算机后，请运行安装程序完成 [name] 的安装。
CannotContinue=安装程序不能继续。请单击“取消”退出。
ApplicationsFound=下列应用程序正在使用需要更新的文件。建议你允许安装程序自动关闭这些应用程序。
ApplicationsFound2=下列应用程序正在使用需要更新的文件。建议你允许安装程序自动关闭这些应用程序。安装完成后，安装程序将尝试重新启动应用程序。
CloseApplications=自动关闭应用程序(&A)
DontCloseApplications=不要关闭应用程序(&D)
ErrorCloseApplications=安装程序无法自动关闭所有应用程序。建议你在继续安装之前，关闭所有使用需要更新的文件的应用程序。

; *** "Installing" wizard page
WizardInstalling=正在安装
InstallingLabel=安装程序正在安装 [name] 到你的计算机，请稍候。

; *** "Setup Completed" wizard page
FinishedHeadingLabel=[name] 安装完成向导
FinishedLabelNoIcons=安装程序已在你的计算机中安装了 [name]。
FinishedLabel=安装程序已在你的计算机中安装了 [name]。可以通过选择安装的快捷方式运行应用程序。
ClickFinish=单击“完成”退出安装程序。
FinishedRestartLabel=为了完成 [name] 的安装，安装程序必须重新启动你的计算机。你想现在重新启动吗？
FinishedRestartMessage=为了完成 [name] 的安装，安装程序必须重新启动你的计算机。%n%n你想现在重新启动吗？
ShowReadmeCheck=是，我想阅读 README 文件
YesRadio=是，立即重新启动计算机(&Y)
NoRadio=否，我稍后重新启动计算机(&N)
; used for example as 'Run MyProg.exe'
RunEntryExec=运行 %1
; used for example as 'View README.txt'
RunEntryShellExec=阅读 %1

; *** "Setup Needs the Next Disk" stuff
ChangeDiskTitle=需要下一个磁盘
SelectDiskLabel2=请插入磁盘 %1 并单击“确定”。%n%n如果这个磁盘中的文件可以在其它文件夹中找到 (不同于下面显示的)，请输入正确的路径或单击“浏览”。
PathLabel=路径(&P):
FileNotInDir2=在 "%2" 中找不到文件 "%1"。请插入正确的磁盘或选择其它文件夹。
SelectDirectoryLabel=请输入下一个磁盘的位置。

; *** Installation phase messages
SetupAborted=安装未完成。%n%n请更正问题后重新运行安装程序。
EntryAbortRetryIgnore=单击“重试”重试，单击“忽略”忽略这个错误继续，或单击“中止”取消安装。

; *** Installation status messages
StatusClosingApplications=正在关闭应用程序...
StatusCreateDirs=正在创建目录...
StatusExtractFiles=正在解压缩文件...
StatusCreateIcons=正在创建快捷方式...
StatusCreateIniEntries=正在创建 INI 条目...
StatusRegisterFiles=正在注册文件...
StatusDeleteFiles=正在删除文件...
StatusRunProgram=正在完成安装...
StatusRestartingApplications=正在重新启动应用程序...
StatusRollback=正在撤销更改...

; *** Misc. errors
ErrorInternal2=内部错误: %1
ErrorFunctionFailedNoCode=%1 失败
ErrorFunctionFailed=%1 失败; 代码 %2
ErrorFunctionFailedWithMessage=%1 失败; 代码 %2.%n%3
ErrorExecutingROW=在执行文件时出错:%n%1