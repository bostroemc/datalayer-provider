# MIT License
#
# Copyright (c) 2020, Bosch Rexroth AG
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os 
import sys
import signal
import time
import sqlite3
from sqlite3 import Error
import json

import datalayer
import datalayerprovider.nodes
import datalayerprovider.utils

connectionProvider = "tcp://boschrexroth:boschrexroth@127.0.0.1:2070"

def run_provider(provider : datalayer.provider.Provider):
    offset = [0, 0]  #Fetch offsets [queue, history]
    
    db = "file:memdb1?mode=memory&cache=shared" #in-memory database used.     
    # db = os.environ.get("SNAP_COMMON") + "/temp.db"
    
    conn = datalayerprovider.utils.initialize(db) #Leave one connection instance open to maintain memory

    node_push = datalayerprovider.nodes.Push(db)  #add job to queue
    node_pop = datalayerprovider.nodes.Pop(db)    #pop job from queue
    node_count = datalayerprovider.nodes.Count(db)     #return queue/pending count, write zero to dump
    node_done =  datalayerprovider.nodes.Done(db)     #add item to db or mark item in db as done
    node_history = datalayerprovider.nodes.History(db)    #fetch items from history

    with datalayer.provider_node.ProviderNode(node_push.cbs, 1234) as node,         \
            datalayer.provider_node.ProviderNode(node_pop.cbs, 1234) as node_2,     \
            datalayer.provider_node.ProviderNode(node_count.cbs, 1234) as node_3,   \
            datalayer.provider_node.ProviderNode(node_done.cbs, 1234) as node_4,    \
            datalayer.provider_node.ProviderNode(node_history.cbs, 1234) as node_5:  
        result = provider.register_node("mechatronics/job_request", node)
        if result != datalayer.variant.Result.OK:
            print("bostroemc: Register job_request failed with: ", result)

        result = provider.register_node("mechatronics/pop", node_2)
        if result != datalayer.variant.Result.OK:
            print("bostroemc: Register pop failed with: ", result)

        result = provider.register_node("mechatronics/count", node_3)
        if result != datalayer.variant.Result.OK:
            print("bostroemc: Register count failed with: ", result)

        result = provider.register_node("mechatronics/done", node_4)
        if result != datalayer.variant.Result.OK:
            print("bostroemc: Register count failed with: ", result)        

        result = provider.register_node("mechatronics/history", node_5)
        if result != datalayer.variant.Result.OK:
            print("bostroemc: Register history failed with: ", result)                

        result= provider.start()
        if result != datalayer.variant.Result.OK:
            print("bostroemc: Starting Provider failed with: ", result)
            
        count=0
        while True:
            count=count+1
            if count > 7199:
                break
            time.sleep(1)
        
        conn.close()     

        result = provider.stop()
 
        result = provider.unregister_node("mechatronics/job_request")
        result = provider.unregister_node("mechatronics/pop")
        result = provider.unregister_node("mechatronics/count")
        result = provider.unregister_node("mechatronics/done")
        result = provider.unregister_node("mechatronics/history")

def run():
    # Create and start ctrlX datalayer...")
    with datalayer.system.System("") as datalayer_system:
        datalayer_system.start(False)

        # Creating provider...
        with datalayer_system.factory().create_provider(connectionProvider) as provider:
            run_provider(provider)

        datalayer_system.stop(True)







        