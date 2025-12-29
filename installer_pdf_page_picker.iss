[Setup]
AppId={{PDFPagePickerMerger}} 
AppName=PDF Page Picker & Merger
AppVersion=1.0.0
AppPublisher=Ha Cong Hieu
DefaultDirName={pf}\PDF Page Picker & Merger
DefaultGroupName=PDF Page Picker & Merger
OutputDir=output
OutputBaseFilename=PDF_Page_Picker_Merger_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=D:\Change\MergePdf\favicon.ico
UninstallDisplayIcon={app}\pdf_page_picker_merge.exe

[Files]
Source: "dist\pdf_page_picker_merge.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PDF Page Picker & Merger"; Filename: "{app}\pdf_page_picker_merge.exe"; IconFilename: "{app}\pdf_page_picker_merge.exe"
Name: "{commondesktop}\PDF Page Picker & Merger"; Filename: "{app}\pdf_page_picker_merge.exe"; IconFilename: "{app}\pdf_page_picker_merge.exe"

[Run]
Filename: "{app}\pdf_page_picker_merge.exe"; Description: "Launch PDF Page Picker & Merger"; Flags: nowait postinstall skipifsilent