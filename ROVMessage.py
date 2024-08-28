#
# La classe ROVMessage specifica gli oggetti messaggio che vengono scambiati tra il ROV e la GND station 
#


import string


separator = "\n"

class ROVMessage():
    
    def __init__(self,msgType,command,value): #costruttore per il comando che voglio creare e inviare
        self.msgType = msgType
        self.command = command
        self.value = value
 
    def Serialize(self): #serializza il messaggio in bytes
        return f"{self.msgType}:{self.command}:{self.value}\n".encode("utf-8")
  
    def GetMsgType(self): # restituisce il tipo di messaggio
        return self.msgType
    
    def ToString(self):
        return f"{self.msgType}:{self.command}:{self.value}"

def ROVMessageFromData(msgString): # crea un nuovo oggetto messaggio dalla stringa
    msgString.replace(separator,"")
    msgType,word,value = msgString.split(":")
    return ROVMessage(msgType,word,value)


#cmd = ROVMessage("COMMAND","SUUS","78")
#data = cmd.Serialize()
#messaggio = ROVMessageFromData(data)
#stringa = messaggio.ToString()
#print(stringa)
        
    

        
        




