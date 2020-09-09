from time import gmtime, strftime, localtime
import paho.mqtt.client as mqtt
import sqlite3
import pandas as pd

transdutor = "transdutor"
dbFile = "data.db"

dataTuple = [-1,-1]

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(transdutor)
    
    
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    theTime = strftime("%Y-%m-%d %H:%M:%S", localtime())
    pressao = (pd.to_numeric(msg.payload)*10 )
    pressao = pressao.round(decimals=2)
    result = (theTime + "\t" + str(pressao))
    print(msg.topic + ":\t" + result)
    if (msg.topic == transdutor):
        dataTuple[0] = str(pressao)
        #return
    if (dataTuple[0] != -1):
        writeToDb(theTime, dataTuple[0])
    return

def writeToDb(theTime, transdutor):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()
    print ("Escrevendo na DB")
    c.execute("INSERT INTO climate VALUES (?,?)", (theTime, transdutor))
    conn.commit()

    global dataTuple
    dataTuple = [-1, -1]

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_forever()
