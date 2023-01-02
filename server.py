import socket
import sys
import pandas as pd
from lxml import etree as et
from xml.etree import cElementTree as cET

data = pd.read_csv('processing_times.csv')
data_array = data.to_numpy()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
ip = '172.20.10.4'
server_address = (ip, 4002)
print(sys.stderr, 'Starting up on ip %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
text_file = open("data.txt", "w")

while True:
    # Wait for a connection
    print('Waiting for a connection...')
    connection, client_address = sock.accept()

    try:
        print('Connection from ip %s port %s.' % server_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(128)

            if data:
                data = data.decode()
                parser = et.XMLParser(recover=True)
                doc = et.fromstring(data, parser=parser)
                xml = et.tostring(doc).decode()

                xml = cET.fromstring(xml)
                carrier_id = str(xml.find('c').text)
                date_time = str(xml.find('d').text)
                station_id = str(xml.find('s').text)
                print('Received XML String:')
                print(data, '\n')
                print('Decoded Data from XML String: ')
                print(' Carrier ID: ', carrier_id)
                print(' Date and Time: ', date_time)
                print(' Station ID: ', station_id)

                carrier_table_id = int(carrier_id) - 1
                station_table_id = int(station_id)
                processing_time = int(data_array[carrier_table_id][station_table_id]) / 1000
                processing_time = str(processing_time)
                print(' Processing Time: ' + processing_time + ' seconds' + '\n')
                connection.sendall(processing_time.encode())
                print('Data Sent to Client: ' + processing_time + '')

                # write string to file
                with open("data.txt", 'a') as text_file:
                    text_file.write(
                        'Carrier ID: ' + carrier_id + '\n' + 'Date and Time: ' + date_time + '\n' + 'Station ID: ' + station_id + '\n' + 'Processing Time: ' + processing_time + '\n\n')

                text_file.close()
                print('Data logged to data.txt.')

            else:
                print('No more data from ip %s port %s. ' % server_address)
                break

    finally:
        # Clean up the connection
        connection.close()
