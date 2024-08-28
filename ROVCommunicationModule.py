import queue
import socket
from ROVMessage import ROVMessage
from ROVMessage import ROVMessageFromData
import threading

SHUTDOWN = False
ip_addr = 'localhost' #127.0.0.1
port = 10000
BUFF_SIZE = 2048
buffer = ""
DATA_CHUNK = 1024

sendingMessagesQueue = queue.Queue(100)
recievingMessagesQueue = queue.Queue(100)

def StartRovCommunicationModule():
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        client.connect((ip_addr,port))
    except Exception as e:
        print(f"errore nello stabilire la connessione: {e}")
        
    print(f"connesso a gnd station all'indirizzo {ip_addr} sulla porta {port}") 
    
    print("avvio del thread di ricezione dati...")
    DataRecieveThread = threading.Thread(target=DataRecievingThread,args=(client,))
    DataRecieveThread.start()
    
    print("avvio del thread di invio dati...")
    DataSenderThread = threading.Thread(target=DataSendingThread,args=(client,))
    DataSenderThread.start()
    
    print("Starting printer thread...")
    PrinterThread = threading.Thread(target=Printer)
    PrinterThread.start()
    
    print("Starting user data sender thread...")
    UsrDataSender = threading.Thread(target=UserDataSender)
    UsrDataSender.start()

    DataRecieveThread.join()
    DataSenderThread.join()
    PrinterThread.join()
    UsrDataSender.join()

def DataRecievingThread(clientEndpoint):
    global SHUTDOWN
    while (not SHUTDOWN):
        if (not recievingMessagesQueue.full()):
            global buffer
            data = clientEndpoint.recv(DATA_CHUNK)
            if not data:
                break
            else:
                buffer += data.decode("utf-8")
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    msgToRecieve = ROVMessageFromData(message)
                    recievingMessagesQueue.put(msgToRecieve)


def DataSendingThread(clientEndpoint):
    global SHUTDOWN
    while (not SHUTDOWN):
        if (not sendingMessagesQueue.empty()):
            msgToSend = sendingMessagesQueue.get()
            clientEndpoint.sendall(msgToSend.Serialize())     

def Printer():
    global SHUTDOWN
    while (not SHUTDOWN):
        if not recievingMessagesQueue.empty():  
            print("coda di ricezione non vuota")
            msg = recievingMessagesQueue.get()
            print(msg.ToString())

def signal_handler():
    print("ctrl+c premuto, interrompo...")
    global SHUTDOWN
    SHUTDOWN = True
    

def UserDataSender():
    global SHUTDOWN
    while not SHUTDOWN:
        msg = input("scrivi il messaggio da inviare>")
        newMss = ROVMessageFromData(msg)
        sendingMessagesQueue.put(newMss)

StartRovCommunicationModule()


    


