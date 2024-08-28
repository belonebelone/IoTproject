from http import server
import signal
import queue
import socket
from ROVMessage import ROVMessage
from ROVMessage import ROVMessageFromData
import queue
import threading

SHUTDOWN = False ##variabile globale che interrompe tutti i cicli

ip_addr = 'localhost' #127.0.0.1
BUFF_SIZE = 2048
buffer = ""
port = 10000
DATA_CHUNK = 1024

sendingMessagesQueue = queue.Queue(100)
recievingMessagesQueue = queue.Queue(100)

def StartGndStationServer():

    signal.signal(signal.SIGINT, signal_handler)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creo una socket
    server.bind((ip_addr,port)) #passo la tupla ip porta per il binding
    server.listen(5) #metto in ascolto il server per le eventuali connessioni in entrata (5 max)
    print(f"in ascolto all' indirizzo {ip_addr} sulla porta {port}")
    
    serverEndpoint,clientAddress = server.accept()

    print(f"connesso al ROV all'indirizzo {clientAddress} sulla porta {port}") 
    
    print("avvio del thread di ricezione dati...")
    DataRecieveThread = threading.Thread(target=DataRecievingThread,args=(serverEndpoint,))
    DataRecieveThread.start()
    
    print("avvio del thread di invio dati...")
    DataSenderThread = threading.Thread(target=DataSendingThread,args=(serverEndpoint,))
    DataSenderThread.start()
    
    print("Starting printer thread...")
    PrinterThread = threading.Thread(target=Printer)
    PrinterThread.start()

    DataRecieveThread.join()
    DataSenderThread.join()
    PrinterThread.join()

                
  
def DataRecievingThread(serverEndpoint):
    global SHUTDOWN
    while (not SHUTDOWN):
        if (not recievingMessagesQueue.full()):
            global buffer
            data = serverEndpoint.recv(DATA_CHUNK)
            if not data:
                break
            else:
                buffer += data.decode("utf-8")
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    msgToRecieve = ROVMessageFromData(message)
                    recievingMessagesQueue.put(msgToRecieve)


def DataSendingThread(serverEndpoint):
    global SHUTDOWN
    while (not SHUTDOWN):
        if (not sendingMessagesQueue.empty()):
            msgToSend = sendingMessagesQueue.get()
            serverEndpoint.sendall(msgToSend.Serialize())     

        
def SendMessage(msgType,word,value):
    msg = ROVMessage(msgType,word,value)
    sendingMessagesQueue.put(msg)
    

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
    
    

StartGndStationServer()



