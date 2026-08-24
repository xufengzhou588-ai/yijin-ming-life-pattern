Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
workspace = fso.GetParentFolderName(WScript.ScriptFullName)
command = "cmd /c cd /d """ & workspace & """ && python server.py"
shell.Run command, 0, False
