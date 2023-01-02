CASE
state
OF

0: // init
IO.xQA1_RIGHT := TRUE;
IO.xMB20 := FALSE;
rfid.ClearError();
ip := '172.20.66.42';
port := 4002;

tcp_client.Connect(sIP := ip, uiPort := port);
state := 1;

1: // wait
for carrier
    IO.xMB20 := FALSE;
    IF
    IO.xBG21 = TRUE
    THEN
    state := 2;
END_IF

2: // wait
for rfid to clear
IF
rfid.xReady
THEN
rfid.Connect(usiNodeId := 32, usiNetworkId := 0, usiChannel := 1); // needs
parameters
state := 3;
END_IF

3: // wait
for rfid to connect
IF
rfid.xReady
THEN
state := 4;
END_IF

4: // read
rfid
tag
rfid.ReadTag(uiStartAddress := 0, uiDataLength := SIZEOF(rfid_data), pData := ADR(rfid_data));
state := 5;

5: // wait
for rfid to read
IF
rfid.xReady
THEN
corrected_ID := dc_ecp.SwapWORD(rfid_data.uiCarrierID);

IF
corrected_ID <= 20
THEN
state := 6;
END_IF
END_IF

6: // read
time and date
get_date_time.xExecute := TRUE;
state := 7;

7: // get
date and time
IF
get_date_time.xDone
THEN
date_time := get_date_time.dtDateAndTime;
date_time_str := DT_TO_STRING(date_time);
timer(IN := TRUE);
state := 8;
END_IF

8: // read
station
id
st_plc := 9;
state := 9;

9: // create
xml
file
xml_str_1 := '<?xml version="1.0"?><root><c>';

xml_str_2 := '</c><d>';

xml_str_3 := '</d><s>';

xml_str_4 := '</s></root>';

xml_file := CONCAT(xml_str_1, DWORD_TO_STRING(corrected_ID));
xml_file := CONCAT(xml_file, xml_str_2);
xml_file := CONCAT(xml_file, date_time_str);
xml_file := CONCAT(xml_file, xml_str_3);
xml_file := CONCAT(xml_file, UINT_TO_STRING(st_plc));
xml_file := CONCAT(xml_file, xml_str_4);
state := 10;

10: // send
to
tcp
server
IF
tcp_client.xConnected
AND
tcp_client.xReady
THEN
state := 11;
END_IF

11: // wait
for carrier
    IF
    IO.xBG21 = TRUE
    THEN
data_out := xml_file;
tcp_client.Send(pToSend := ADR(data_out), uiSizeToSend := SIZEOF(data_out));
data_in := '0';
state := 12;
END_IF

12: // wait
for send
    IF
    tcp_client.xReady
    THEN
tcp_client.Receive(pToReceive := ADR(data_in), uiSizeToReceive := SIZEOF(data_in));
state := 13;
END_IF

13:
PT_str_1 := 'T#0';
PT_str_2 := 's';
PT_str := CONCAT(PT_str_1, data_in);
PT_str := CONCAT(PT_str, PT_str_2);
PT_val := STRING_TO_TIME(PT_str);

timer(IN := TRUE, PT := PT_val);
state := 14;

14: // wait
for receive
    IF
    tcp_client.xReady
    AND
    timer.Q = TRUE
    THEN
timer(IN := FALSE);
state := 15;
END_IF

15: // wait
for carrier to pass
IO.xMB20 := TRUE;

IF
IO.xBG21 = FALSE
THEN
timer(IN := FALSE);
IO.xMB20 := FALSE;
state := 1;
END_IF

END_CASE
rfid();
get_date_time();
timer();
tcp_client();
