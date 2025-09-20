Set i1 = CreateObject("InitHolder")                   ''''''''''''''''''''''
Set o1 = CreateObject("Pipe")                         '  try to activate   '
Set txtWnd = CreateObject("ViewDesk")                 '      objects       '
Set iso = CreateObject("ISOMessage")                  '                    '
Set buff   = CreateObject("BufAccess")                ''''''''''''''''''''''

Dim Red, Blue, Green, Violet, Orange, Grey
SetColors

i1.SetFileName("HostEmulator.ini")
'i1.SetFileName("HostEmulator_PRV.ini")

host = "ISO Host Emulator"
txtWnd.Init i1, host

o1.Init i1, "com"

Connect = i1.GetString ("Pipe_com", "Port Type", "serial")
If Connect = "ip" Then 
    IsIp = True
Else 
    IsIp = False
End If

res = o1.Open                     '''''''''''''''''''''''''''''''''
If res = False Then               '                               '
    txtWnd.CloseDesk              '        try to open Port       '
    MsgBox o1.GetError            '         for connection        '
End If                            '''''''''''''''''''''''''''''''''

InputBuf = 0
OutputBuf = 1

iso.Init i1, "ISO"                ' get format and other params from ini-file

'iso.SetSettlement False          ' you can switch off settlement decoding
'iso.SetField63Decoded False      ' you can switch off Parsing 63 field

txtWnd.ColoredWrite "Host ISO", Grey
txtWnd.ColoredWrite "Port: " + o1.InitString + " was opened", Orange


'txtWnd.IsLogToFile = False       ' you can switch off logging to file
'txtWnd.IsLogToScreen = False     ' you can switch off logging to screen

For a = 0 To 1000000

    Do Until False                                    '   Endless loop     '
        iso.SetAutoDate True                          ' you have to switch on AutoSet Date and Time (Fields 12 and 13)
                                                      ' it may be switch off when decoding Adjust Sale
        Repeat = 0
        SizeReq = 0
        Do
            If txtWnd.IsClosed = True Then Exit For   ' Check Exit button  '
            If o1.GetStatus() Then txtWnd.ColoredWrite o1.GetStatusString(), Grey

            If SizeReq = 0 Then                                       ''''''''''''''''''''''
                SizeReq = o1.Read(InputBuf, 1024, 100, 0)             '    Read message    '
            Else                                                      '     from port      '
                SizeReq = SizeReq + o1.Read(InputBuf, 1024-SizeReq, 100, SizeReq)          '
                Repeat = Repeat + 1                                   '                    '
            End If                                                    ''''''''''''''''''''''

        Loop Until (SizeReq <> 0) And (Repeat > 3)
                                                                      ''''''''''''''''''''''
        If buff.CheckFrame(o1, InputBuf, SizeReq, IsIp) = False Then  '       Check        '
            txtWnd.ShowColoredTrace o1, InputBuf, 0, SizeReq, "Corrupted message was received", Red
        Else                                                          '      framing       '
            txtWnd.ShowColoredTrace o1, InputBuf, 0, SizeReq, "Request ", Violet           '
        End If                                                        ''''''''''''''''''''''
                                                                      ''''''''''''''''''''''
        CountFields = iso.Decode (o1, InputBuf, 8 + CInt(IsIp), SizeReq-8-CInt(IsIp))      '
        If CountFields = 0 Then                                       '                    '
            e = iso.GetError                                          '   Decode message   '
            txtWnd.Write(e)                                           '                    '
        End If                                                        ''''''''''''''''''''''

        Call CreateResponse   ' !!!!!!!!!!!!!!!!!!!!!!! MAIN SUBROUTINE !!!!!!!!!!!!!!!!!!!!!!!!!!!!

        txtWnd.ShowColoredMessage iso, True, Violet
        CheckField55                                                  ' Check Mandatory Tags Field 55

        SizeRes = iso.Encode (o1, OutputBuf, 0)                       ''''''''''''''''''''''
        If SizeRes = 0 Then                                           '                    '
            e = iso.GetError                                          '   Encode message   '
            txtWnd.Write e                                            '                    '
            Exit Do                                                   '                    '
        End If                                                        ''''''''''''''''''''''
                                                                      ''''''''''''''''''''''
        SizeRes = buff.SwapTPDU(o1, OutputBuf, o1, InputBuf, SizeRes, IsIp)' Create TPDU   '
        SizeRes = buff.Frame(o1, OutputBuf, SizeRes, IsIp)            '   Create framing   '
                                                                      ''''''''''''''''''''''
        txtWnd.ShowColoredTrace o1, OutputBuf, 0, SizeRes, "Response", Blue

        CountFields = iso.Decode (o1, OutputBuf, 8 + CInt(IsIp), SizeRes-8-CInt(IsIp))
        txtWnd.ShowColoredMessage iso, True, Blue

        o1.Write OutputBuf, SizeRes, 0                                ' Send message to port

    Loop

Next


''''''''''''' CREATE RESPONSE ''''''''''''''''''

Sub CreateResponse

strMsgType = iso.GetField(0)
strProcessingCode = iso.GetField(3)
strTrack2 = iso.GetField(35)
strTxnCurrency = iso.GetField(49)
strNII = iso.GetField(24)
strAmt = iso.GetField(4)

MsgErr = " not present. ERROR"

If (strMsgType = "0100" And Mid(strProcessingCode, 1, 2) = "00" And Mid(strProcessingCode, 4, 2) = "00") Then
    ColoredReport "Authorization", Violet
    Call Message
    'Addend to response 
    iso.SetField 0, "0110"                 ' MsgType
    iso.SetField 3, "000000"               ' ProcessingCode
	RRN = CStr(Int(1000000000000*Rnd))
	iso.SetField 37, RRN
	AUTHC = CStr(Int(1000000*Rnd))
	iso.SetField 38, AUTHC
	iso.SetField 39, "00"
    
ElseIf (strMsgType = "0100" And Mid(strProcessingCode, 1, 2) = "30" And Mid(strProcessingCode, 4, 2) = "00")Then
    ColoredReport "Pre-Authorization", Violet
    Call Message
    'Addend to response    
    iso.SetField 0, "0110"                 ' MsgType
    iso.SetField 3, "300000"               ' ProcessingCode
	iso.SetField 37, "123456789012"
	iso.SetField 39, "00"
	
ElseIf (strMsgType = "0100" And Mid(strProcessingCode, 1, 2) = "38" And Mid(strProcessingCode, 4, 2) = "00")Then
    ColoredReport "Infocall", Violet
    Call Message
    'Addend to response    
    iso.SetField 0, "0110"                 ' MsgType
    iso.SetField 3, "380000"               ' ProcessingCode
'	iso.setHex2Field 63, "0084323202d7d3c2c0ca2120c4cec1c0c2cbc5cd20d2c5c320c4cbdf20cec1cdcec2cbc5cdc8df20d7c5d0c5c720c8cdd4cecacecb20c6c4c820cec1cdcec2cbc5cdc8df1C4C4F414444323032353039313731363035" '"008522023232444E30343830415620CDC5D220D2C0CACEC3CE20534E20C220D1CFC8D1CAC520D0C0C7D0C5D8C5CDCDDBD52020534E3A20303238322D3737392D3939381C4C4F414444323032313131313231343038"	
    iso.setHex2Field 63, "010632320104444E3034313038304B415620CDC5D220D2C0CACEC3CE20534E20C220D1CFC8D1CAC520D0C0C7D0C5D8C5CDCDDBD52020534E3A303238332D3737382D3433362050503A3930322D3537342D3334363C71723E363636204156452068656C6C6F3C2F71723E" 'QR 3C71723E → <qr>
'	iso.setHex2Field 63, "00193232494e495444323032353039313731353537" 'init infocall

'ElseIf (strMsgType = "0200" And Mid(strProcessingCode, 1, 2) = "00" And Mid(strProcessingCode, 4, 2) = "00" And strTxnCurrency = "840")Then
'    ColoredReport "Sale+DCC2", Violet
'    Call Message
'    Addend to response
'    iso.SetField 0, "0210"                 ' MsgType
'    iso.SetField 3, "000000"               ' ProcessingCode
'	iso.SetField 4, "000000014616" 
'	iso.SetField 37, "123456789012"
'	iso.SetField 39, "05"
'	iso.SetTagFld55 "8A", "05"
'	iso.setField 57, "014371163074562330039300177630116325744305102184TID=301163257443051"
'	iso.setHex2Field 63, "00442e42323256455249464f4e452e5435505256615f3033542e303333302d3332352d3537392e38393338303033"   

'ElseIf (strMsgType = "0200" And Mid(strProcessingCode, 1, 2) = "00" And Mid(strProcessingCode, 4, 2) = "00")Then
'    ColoredReport "Sale+DCC1", Violet
'    Call Message
'    Addend to response
'    iso.SetField 0, "0210"                 ' MsgType
'    iso.SetField 3, "000000"               ' ProcessingCode
'	iso.SetField 39, "00"
'	iso.SetField 49, "980"
'	iso.setField 57, "126950000000003198106319440000000000000000000004840704190000000000000000000000497870380000000000000000000001009806100000000000000" ' DCC
'	iso.setHex2Field 63, "00650063323956455249464F4E451C5435505256615F3033551C303333312D3233342D3530331C383933383030333939303239393537373937351C3034310000000000" 

ElseIf (strMsgType = "0200" And Mid(strProcessingCode, 1, 2) = "00" And Mid(strProcessingCode, 4, 2) = "00" And strAmt = "000000000000")Then
    ColoredReport "Service", Violet
    Call Message
'    Addend to response
    iso.SetField 0, "0210"                 ' MsgType
    iso.SetField 3, "000000"               ' ProcessingCode
	iso.SetField 4, "000000000000"
	iso.SetField 39, "00"
	iso.setHex2Field 63, "0953383949443A20323630373539303320202020202020205F5F5F5F5F5F5F5F5F5F5FC5CAC7C5CCCFCBDFD0D1CED44949C2D1DCCAC020C1CED0D9C0C349C22DCAC0202020202020202020202020202020202020CBC0C1CED0C0D2CED0CDC020C449C0C3CDCED12DD2C8CAC020CFCF20202020202020202020202020D02FD03A205541323633303532393930303030303236303036303336373034363233202020202020CBC0C1CED0C0D2CED0CDC020C449C0C3CDCED12DD2C8CAC020CFCF20202020202020202020202020CCD4CE3A20202020202020202020202020202020D1C8CCC2CECB20CAC0D1CFCBC0CDD33A20303220CDCECC49CDC0CBC820202020202020202020202031202D203120202020202020202020202020202032202D203020202020202020202020202020202035202D20302020202020202020202020202020203130202D203020202020202020202020202020203230202D203120202020202020202020202020203530202D20312020202020202020202020202020313030202D203520202020202020202020202020323030202D203235202020202020202020202020353030202D20333420202020202020202020202031303030202D2032202020202020202020202020CCCECDC5D2202D2031302C303020C3D0CD202020D1D3CCC020D0C0C7CECC3A20202020202020202032343538312C303020C3D0CD202020202020202028C4C2C0C4D6DFD2DC20D7CED2C8D0C820D2C82DD1DFD74920CF27DFD2D1CED220C249D149CCC4C5D1DFD220CEC4CDC020C3D0CD2E20303020CACECF2E29202020202020202020202020202020202020C3C0D0C0D7C020CB49CD49DF20C7202020202020CFC8D2C0CDDC2049CDCAC0D1C0D64949202020203020383030203530302038303720202020202020CAC0D1C8D03A20202020202020202020202020205F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5FCECFCBCECCC1CEC2C0CDD3202020202020202020D1D3CCCAD320B920313037333439202020202020C1C5C720CFC5D0C5D0C0D5D3CDCAD32020202020C2CACBC0C4C5CDC8D520C220CDC5492020202020CACED8D249C22020202020202020202020202020CFD0C8C9CDDFC22049CDCAC0D1C0D2CED03A20205F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5FCACECDD2D0CECBC5D03A202020202020202020205F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5FCACEC420CF49C4D2C2C5D0C4C6C5CDCDDF20202049CDCAC0D1C0D649493A203236303735393033203C71723E69643D32363037353930333B6261673D3130373334393C2F71723E"  

ElseIf (strMsgType = "0200" And Mid(strProcessingCode, 1, 2) = "00" And Mid(strProcessingCode, 4, 2) = "00")Then
    ColoredReport "Sale/Debit", Violet
    Call Message
'    Addend to response
    iso.SetField 0, "0210"                 ' MsgType
    iso.SetField 3, "000000"               ' ProcessingCode
'	iso.SetField 4, "000000643700"
	iso.SetField 23, "000"
	RRN = CStr(Int(1000000000000*Rnd))
	iso.SetField 37, RRN
	AUTHC = CStr(Int(1000000*Rnd))
	iso.SetField 38, AUTHC
	iso.SetField 39, "00"
	iso.SetField 49, "980"
	iso.SetTagFld55 "8A", "00"
'	iso.setField 57, "01530C00000000150001531D00000000028200532980003930"
'	iso.setField 57, "0143712491582265400393001576MSIXPZF58090601984TID=MSIXPZF580906"
	iso.setField 57, "01530C000000000375003930" 'Discount
'	iso.SetField 57, "014371163074562330039300177630116325744305102184TID=301163257443051"
'	iso.setHex2Field 63, "00882e42323256455249464f4e452e5435505256615f3033542e303333302d3332352d3537392e38393338303033"
'	iso.setHex2Field 63, "0953383949443A20323630373539303320202020202020205F5F5F5F5F5F5F5F5F5F5FC5CAC7C5CCCFCBDFD0D1CED44949C2D1DCCAC020C1CED0D9C0C349C22DCAC0202020202020202020202020202020202020CBC0C1CED0C0D2CED0CDC020C449C0C3CDCED12DD2C8CAC020CFCF20202020202020202020202020D02FD03A205541323633303532393930303030303236303036303336373034363233202020202020CBC0C1CED0C0D2CED0CDC020C449C0C3CDCED12DD2C8CAC020CFCF20202020202020202020202020CCD4CE3A20202020202020202020202020202020D1C8CCC2CECB20CAC0D1CFCBC0CDD33A20303220CDCECC49CDC0CBC820202020202020202020202031202D203120202020202020202020202020202032202D203020202020202020202020202020202035202D20302020202020202020202020202020203130202D203020202020202020202020202020203230202D203120202020202020202020202020203530202D20312020202020202020202020202020313030202D203520202020202020202020202020323030202D203235202020202020202020202020353030202D20333420202020202020202020202031303030202D2032202020202020202020202020CCCECDC5D2202D2031302C303020C3D0CD202020D1D3CCC020D0C0C7CECC3A20202020202020202032343538312C303020C3D0CD202020202020202028C4C2C0C4D6DFD2DC20D7CED2C8D0C820D2C82DD1DFD74920CF27DFD2D1CED220C249D149CCC4C5D1DFD220CEC4CDC020C3D0CD2E20303020CACECF2E29202020202020202020202020202020202020C3C0D0C0D7C020CB49CD49DF20C7202020202020CFC8D2C0CDDC2049CDCAC0D1C0D64949202020203020383030203530302038303720202020202020CAC0D1C8D03A20202020202020202020202020205F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5FCECFCBCECCC1CEC2C0CDD3202020202020202020D1D3CCCAD320B920313037333439202020202020C1C5C720CFC5D0C5D0C0D5D3CDCAD32020202020C2CACBC0C4C5CDC8D520C220CDC5492020202020CACED8D249C22020202020202020202020202020CFD0C8C9CDDFC22049CDCAC0D1C0D2CED03A20205F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5FCACECDD2D0CECBC5D03A202020202020202020205F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5FCACEC420CF49C4D2C2C5D0C4C6C5CDCDDF20202049CDCAC0D1C0D649493A203236303735393033203C71723E69643D32363037353930333B6261673D3130373334393C2F71723E"  
'	iso.setHex2Field 63, "0084323202d7d3c2c0ca2120c4cec1c0c2cbc5cd20d2c5c320c4cbdf20cec1cdcec2cbc5cdc8df20d7c5d0c5c720c8cdd4cecacecb20c6c4c820cec1cdcec2cbc5cdc8df1C4C4F414444323032343031313931363435" 'тег для обновления
'	iso.setHex2Field 63, "00193232494e495444323032353033313131353135" 'Init
'	iso.setHex2Field 63, "0102323950415353504F52543A20424C41424C41424C412E20564944414E20424C55424C55424C552030312E30312E3139303120676F64612E2071776572747975696F706173646667686A6B6C2071776572747975696F6F6F202D203130302073696D766F6C6F76"
	iso.setHex2Field 63, "00 42 32 32 56 45 52 49 46 4F 4E 45 1C 54 35 50 52 56 61 5F 30 34 4D 1C 30 32 36 31 2D 32 30 31 2D 34 30 37 1C 38 39 33 38 30 30 33"
'	iso.setHex2Field 63, "00 88 1C 42 32 32 56 45 52 49 46 4F 4E 45 1C 54 35 50 52 56 61 5F 30 33 54 1C 30 33 33 30 2D 33 32 35 2D 35 37 39 1C 38 39 33 38 30 30 33"
	
ElseIf (strMsgType = "0200" And Mid(strProcessingCode, 1, 2) = "20" And Mid(strProcessingCode, 4, 2) = "00")Then
    ColoredReport "Refund", Violet
    Call Message    
    'Addend to response
    iso.SetField 0, "0210"                 ' MsgType
    iso.SetField 3, "200001"               ' ProcessingCode
	iso.SetField 39, "00"
'	iso.setHex2Field 63, "0102323950415353504F52543A20424C41424C41424C412E20564944414E20424C55424C55424C552030312E30312E3139303120676F64612E2071776572747975696F706173646667686A6B6C2071776572747975696F6F6F202D203130302073696D766F6C6F76"
    
ElseIf (strMsgType = "0200" And Mid(strProcessingCode, 1, 2) = "01" And Mid(strProcessingCode, 4, 2) = "00")Then
    ColoredReport "Cash", Violet
    Call Message
    iso.SetField 0, "0210"                 ' MsgType
    iso.SetField 3, "010000"               ' ProcessingCode
	iso.SetField 39, "00"
	iso.setHex2Field 63, "0008333730303030303200143339303030303030303031313038"
 
 ElseIf (strMsgType = "0200" And Mid(strProcessingCode, 1, 2) = "21" And Mid(strProcessingCode, 4, 2) = "00")Then
    ColoredReport "Deposit", Violet
    Call Message
    iso.SetField 0, "0210"                 ' MsgType
    iso.SetField 3, "210000"               ' ProcessingCode
	iso.SetField 39, "00"
'	iso.setHex2Field 63, "0408323950415353504F52543A20424C41424C41424C412E20564944414E20424C55424C55424C552030312E30312E3139303120676F64612E2071776572747975696F706173646667686A6B6C2071776572747975696F6F6F202D203130302073696D766F6C6F76323950415353504F52543A20424C41424C41424C412E20564944414E20424C55424C55424C552030312E30312E3139303120676F64612E2071776572747975696F706173646667686A6B6C2071776572747975696F6F6F202D203130302073696D766F6C6F76323950415353504F52543A20424C41424C41424C412E20564944414E20424C55424C55424C552030312E30312E3139303120676F64612E2071776572747975696F706173646667686A6B6C2071776572747975696F6F6F202D203130302073696D766F6C6F76323950415353504F52543A20424C41424C41424C412E20564944414E20424C55424C55424C552030312E30312E3139303120676F64612E2071776572747975696F706173646667686A6B6C2071776572747975696F6F6F202D203130302073696D766F6C6F76"
   
ElseIf (strMsgType = "0200" And Mid(strProcessingCode, 1, 2) = "09" And Mid(strProcessingCode, 4, 2) = "00")Then
    ColoredReport "Sale & Cash", Violet
    Call Message
    iso.SetField 0, "0210"                 ' MsgType
    iso.SetField 3, "090000"               ' ProcessingCode
	iso.SetField 39, "00"
	iso.setField 57, "01530C000000000255003930"
ElseIf (strMsgType = "0200" And Mid(strProcessingCode, 1, 2) = "02" And Mid(strProcessingCode, 4, 2) = "00")Then
    ColoredReport "Void, Sale, on-line", Violet
    Call Message
    iso.SetField 0, "0210"                 ' MsgType
    iso.SetField 3, "020000"               ' ProcessingCode
	iso.SetField 39, "00"
ElseIf (strMsgType = "0220" And Mid(strProcessingCode, 1, 2) = "02" And Mid(strProcessingCode, 4, 2) = "00")Then
    ColoredReport "Adjust Sale", Violet
    iso.SetAutoDate False     ' you have to switch off AutoSet Date and Time (Fields 12 and 13)
    If (iso.GetField(38) = "") Then ColoredReport "Auth. Id. Response is not present. ERROR", Red
    iso.SetField 0, "0230"                 ' MsgType
    iso.SetField 3, "020000"               ' ProcessingCode
    ' Check mandatory fields
    If (iso.GetField(4) = "") Then ColoredReport "Amount not specified", Red
    strTraceNo = iso.GetField(11)
    If (strTraceNo = "") Then ColoredReport "System Trace Number" + MsgErr, Red
    strNII = iso.GetField(24)
    If (strNII = "") Then ColoredReport "NII" + MsgErr, Red
    strTerminalID = iso.GetField(41)
    If (strTerminalID = "") Then ColoredReport "Terminal ID" + MsgErr, Red
    If (iso.GetField(42) = "") Then ColoredReport "Acquirer ID" + MsgErr, Red

    ' Form the response
    iso.SetField 11, strTraceNo            ' TraceNo
    iso.SetField 24, strNII                ' NII
    iso.SetField 37, "000000000015"        ' RetRefNo
    iso.SetField 39, "00"                  ' ResponseCode
    iso.SetField 41, strTerminalID         ' TerminalID
ElseIf (strMsgType = "0220" And Mid(strProcessingCode, 1, 2) = "00" And Mid(strProcessingCode, 4, 2) = "00")Then
    ColoredReport "Off-Line Sale", Violet
    If (iso.GetField(38) = "") Then ColoredReport "Auth. Id. Response" + MsgErr, Red
    Call Message
    iso.SetField 0, "0230"                 ' MsgType
    iso.SetField 3, "000000"               ' ProcessingCode
ElseIf (strMsgType = "0220" And Mid(strProcessingCode, 1, 2) = "20" And Mid(strProcessingCode, 4, 2) = "00")Then
    ColoredReport "Off-Line Refund or Sales Completion", Violet
    If (iso.GetField(38) = "") Then ColoredReport "Auth. Id. Response" + MsgErr, Red
    Call Message
    iso.SetField 0, "0230"                 ' MsgType
    iso.SetField 3, "200000"               ' ProcessingCode

ElseIf (strMsgType = "0400" ) Then
    ColoredReport "Reversal", Violet
    If (iso.GetField(25) = "") Then ColoredReport "POSConditionCode" + MsgErr, Red
    Call Message    
    iso.SetField 0, "0410"                 ' MsgType
    iso.SetField 3, strProcessingCode      ' ProcessingCode
	iso.SetField 39, "00"

ElseIf (strMsgType = "0800" And Mid(strProcessingCode, 1, 2) = "99" And Mid(strProcessingCode, 4, 2) = "00")Then
    ColoredReport "Test Transaction", Violet
    strNII = iso.GetField(24)
    If (strNII = "") Then ColoredReport "NII" + MsgErr, Red
    strTerminalID = iso.GetField(41)
    If (strTerminalID = "") Then ColoredReport "Terminal ID" + MsgErr, Red
    
    iso.SetField 0, "0810"                 ' MsgType
    iso.SetField 3, "990000"               ' ProcessingCode
	iso.SetField 11, strTraceNo            ' TraceNo
    iso.SetField 24, strNII                ' NII
	AUTHC = CStr(Int(1000000*Rnd))
	iso.SetField 38, AUTHC
	iso.SetField 39, "00"                  ' ResponseCode -> Bad settlement
    iso.SetField 41, strTerminalID         ' TerminalID

ElseIf (strMsgType = "0500" And Mid(strProcessingCode, 1, 2) = "92" And Mid(strProcessingCode, 4, 2) = "00")Then
    ColoredReport "Settlement", Violet
    strTraceNo = iso.GetField(11)
    If (strTraceNo = "") Then ColoredReport "System Trace Number" + MsgErr, Red
    strNII = iso.GetField(24)
    If (strNII = "") Then ColoredReport "NII" + MsgErr, Red
    strTerminalID = iso.GetField(41)
    If (strTerminalID = "") Then ColoredReport "Terminal ID" + MsgErr, Red
    If (iso.GetField(42) = "") Then ColoredReport "Acquirer ID" + MsgErr, Red
    
    iso.SetField 0, "0510"                 ' MsgType
    iso.SetField 3, "920000"               ' ProcessingCode
    iso.SetField 11, strTraceNo            ' TraceNo
    iso.SetField 24, strNII                ' NII
    iso.SetField 39, "00"                  ' ResponseCode -> Bad settlement
    iso.SetField 41, strTerminalID         ' TerminalID
    
ElseIf (strMsgType = "0500" And Mid(strProcessingCode, 1, 2) = "96" And Mid(strProcessingCode, 4, 2) = "00")Then
    ColoredReport "Settlement Trailer", Violet
    strTraceNo = iso.GetField(11)
    If (strTraceNo = "") Then ColoredReport "System Trace Number" + MsgErr, Red
    strNII = iso.GetField(24)
    If (strNII = "") Then ColoredReport "NII" + MsgErr, Red
    strTerminalID = iso.GetField(41)
    If (strTerminalID = "") Then ColoredReport "Terminal ID" + MsgErr, Red
    If (iso.GetField(42) = "") Then ColoredReport "Acquirer ID" + MsgErr, Red

    iso.SetField 0, "0510"                 ' MsgType
    iso.SetField 3, "960000"               ' ProcessingCode
    iso.SetField 11, strTraceNo            ' TraceNo
    iso.SetField 24, strNII                ' NII
    iso.SetField 37, "000000000016"        ' RetRefNo
    iso.SetField 39, "00"                  ' ResponseCode
    iso.SetField 41, strTerminalID         ' TerminalID
    
ElseIf (strMsgType = "0320" And Mid(strProcessingCode, 1, 2) <> "90")Then
    ColoredReport "Batch Upload", Violet
    If (iso.GetField(22) = "") Then ColoredReport "POSEntryMode" + MsgErr, Red
    If (iso.GetField(25) = "") Then ColoredReport "POSConditionCode" + MsgErr, Red
    If (iso.GetField(37) = "") Then ColoredReport "retrieval RefNo" + MsgErr, Red
    
    Call Message
    iso.SetField 0, "0330"                 ' MsgType
    iso.SetField 3, "030000"               ' ProcessingCode
	iso.SetField 39, "00"

ElseIf (strMsgType = "0800" And Mid(strProcessingCode, 1, 2) = "91" And Mid(strProcessingCode, 4, 2) = "00")Then
    ColoredReport "Statistics", Violet
    strTraceNo = iso.GetField(11)
    If (strTraceNo = "") Then ColoredReport "System Trace Number" + MsgErr, Red
    strNII = iso.GetField(24)
    If (strNII = "") Then ColoredReport "NII" + Error, Red
    strTerminalID = iso.GetField(41)
    If (strTerminalID = "") Then ColoredReport "Terminal ID" + MsgErr, Red
        
    iso.SetField 0, "0810"                 ' MsgType
    iso.SetField 3, "910000"               ' ProcessingCode
    iso.SetField 11, strTraceNo            ' TraceNo
    iso.SetField 24, strNII                ' NII
    iso.SetField 39, "00"                  ' ResponseCode
    iso.SetField 41, strTerminalID         ' TerminalID
    iso.SetField 63, "010302072100000208707700717FFFFFFFFFFFFF" ' ScheduleCommand
    
Else
    ColoredReport "Unknown message type", Red

    intMsgType = CInt(strMsgType)
    iso.SetField 0, CStr(intMsgType+10)    ' MsgType
    iso.SetField 3, strProcessingCode      ' ProcessingCode
    If (iso.GetField(4) <> "") Then iso.SetField 4, iso.GetField(4)    ' TxnAmount
    If (iso.GetField(11) <> "") Then iso.SetField 11, iso.GetField(11) ' STAN
    If (iso.GetField(24) <> "") Then iso.SetField 24, iso.GetField(24) ' NII
    iso.SetField 37, "000000000013"        ' RetRefNo
    iso.SetField 39, "00"                  ' ResponseCode
    If (iso.GetField(41) <> "") Then iso.SetField 41, iso.GetField(41) ' TerminalID
End If

End Sub

'''''''''''''''''''''''''''' Message '''''''''''''''''''''''''''''''''''''''
Sub Message
MsgErr = " not present. ERROR"
    ' Check mandatory fields
    If (iso.GetField(4) = "") Then ColoredReport "Amount not specified", Red
    strTraceNo = iso.GetField(11)
    If (strTraceNo = "") Then ColoredReport "System Trace Number" + MsgErr, Red
    strNII = iso.GetField(24)
    If (strNII = "") Then ColoredReport "NII" + MsgErr, Red
    strTerminalID = iso.GetField(41)
    If (strTerminalID = "") Then ColoredReport "Terminal ID" + MsgErr, Red
    If (iso.GetField(42) = "") Then ColoredReport "Acquirer ID" + MsgErr, Red
        
    ' Form the response
    iso.SetField 11, strTraceNo            ' TraceNo
    iso.SetField 24, strNII                ' NII
    iso.SetField 37, "000000000014"        ' RetRefNo
'    iso.SetField 38, "000000"              ' AutnID
'    iso.SetField 39, "00"                  ' ResponseCode
    iso.SetField 41, strTerminalID         ' TerminalID
End Sub

'''''''''''''''''''''''''' ColoredReport '''''''''''''''''''''''''''''''''''
Function ColoredReport (String, Color)
    Name = "STIM"
'   MsgBox string, 4096, Name
    txtWnd.ColoredWrite String, Color
End Function

'''''''''''''''''''''''''' SetColors '''''''''''''''''''''''''''''''''''
Function SetColors
    Red     = 1
    Blue    = 2
    Green   = 3
    Violet  = 4
    Orange  = 5
    Grey    = 6
End Function

'''''''''''''''''''''''''' CheckField55 '''''''''''''''''''''''''''''''''''
Function CheckField55
    If (iso.GetField(55) <> "") Then
        If(iso.GetTagFld55("5F2A") = "") Then ColoredReport "Mandatory tag 5F2A is not present. ERROR", Red
        If(iso.GetTagFld55("82") = "") Then ColoredReport "Mandatory tag 82 is not present. ERROR", Red
        If(iso.GetTagFld55("95") = "") Then ColoredReport "Mandatory tag 95 is not present. ERROR", Red
        If(iso.GetTagFld55("9A") = "") Then ColoredReport "Mandatory tag 9A is not present. ERROR", Red
        If(iso.GetTagFld55("9C") = "") Then ColoredReport "Mandatory tag 9C is not present. ERROR", Red
        If(iso.GetTagFld55("9F02") = "") Then ColoredReport "Mandatory tag 9F02 is not present. ERROR", Red
'        If(iso.GetTagFld55("9F03") = "") Then ColoredReport "Mandatory tag 9F03 is not present. ERROR", Red
        If(iso.GetTagFld55("9F10") = "") Then ColoredReport "Mandatory tag 9F10 is not present. ERROR", Red
        If(iso.GetTagFld55("9F1A") = "") Then ColoredReport "Mandatory tag 9F1A is not present. ERROR", Red
        If(iso.GetTagFld55("9F26") = "") Then ColoredReport "Mandatory tag 9F26 is not present. ERROR", Red
        If(iso.GetTagFld55("9F27") = "") Then ColoredReport "Mandatory tag 9F27 is not present. ERROR", Red
        If(iso.GetTagFld55("9F36") = "") Then ColoredReport "Mandatory tag 9F36 is not present. ERROR", Red
        If(iso.GetTagFld55("9F37") = "") Then ColoredReport "Mandatory tag 9F37 is not present. ERROR", Red
    End If
End Function
