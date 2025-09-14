' Download file subroutine
Sub DownloadFile(url, target)
    Const adTypeBinary = 1
    Const adSaveCreateOverWrite = 2
    Dim http, ado

    ' Create XMLHTTP object
    Set http = CreateObject("Msxml2.XMLHTTP")
    http.open "GET", url, False
    http.send

    ' Check request status
    If http.Status = 200 Then
        ' Create ADODB.Stream object
        Set ado = CreateObject("Adodb.Stream")
        ado.Type = adTypeBinary
        ado.Open
        ado.Write http.responseBody
        ado.SaveToFile target, adSaveCreateOverWrite
        ado.Close
        WScript.Echo "[+] File downloaded successfully, saved as: " & target
    Else
        WScript.Echo "[!] Download failed, HTTP status code: " & http.Status
    End If
End Sub

' Get command line arguments
Set args = WScript.Arguments
If args.Count <> 2 Then
    WScript.Echo "Usage: cscript Download.vbs <URL-FILE> <SAVE-PATH>"
    WScript.Quit 1
End If

' Assign command line arguments
url = args(0)
target = args(1)

' Call download subroutine
DownloadFile url, target
