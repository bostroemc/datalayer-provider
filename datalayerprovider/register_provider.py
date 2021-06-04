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
import datalayerprovider.database_utils

connectionProvider = "tcp://boschrexroth:boschrexroth@127.0.0.1:2070"

def run_provider(provider : datalayer.provider.Provider):

    print("bostroemc: Starting provider...")
    queue = []
    
    db = os.environ.get("SNAP_COMMON") + "/temp.db"  # "/var/snap/datalayer-provider/common/temp.db"   
    conn = datalayerprovider.database_utils.initialize(db)
    job_order = {"name": ["carl", "bostroem"]}
    datalayerprovider.database_utils.add_job_order(conn, json.dumps(job_order))
    datalayerprovider.database_utils.add_job_order(conn, json.dumps(job_order))
    datalayerprovider.database_utils.add_job_order(conn, json.dumps(job_order))

    node_push = datalayerprovider.nodes.Push(queue, conn)  #add job to queue
    node_pop = datalayerprovider.nodes.Pop(queue, conn)    #pop job from queue
    node_count = datalayerprovider.nodes.Count(queue, conn)     #return queue/pending count
    node_dump = datalayerprovider.nodes.Dump(queue, conn)      #dump queue
    # node_fetch = datalayerprovider.my_provider_node.Fetch(queue)    #fetch items from db
    node_done =  datalayerprovider.nodes.Done(queue, conn)     #add item to db or mark item in db as done


    with datalayer.provider_node.ProviderNode(node_push.cbs, 1234) as node,         \
            datalayer.provider_node.ProviderNode(node_pop.cbs, 1234) as node_2,     \
            datalayer.provider_node.ProviderNode(node_count.cbs, 1234) as node_3,   \
            datalayer.provider_node.ProviderNode(node_dump.cbs, 1234) as node_4,    \
            datalayer.provider_node.ProviderNode(node_done.cbs, 1234) as node_5:
        result = provider.register_node("mechatronics/job_request", node)
        if result != datalayer.variant.Result.OK:
            print("bostroemc: Register job_request failed with: ", result)

        result = provider.register_node("mechatronics/pop", node_2)
        if result != datalayer.variant.Result.OK:
            print("bostroemc: Register pop failed with: ", result)

        result = provider.register_node("mechatronics/count", node_3)
        if result != datalayer.variant.Result.OK:
            print("bostroemc: Register count failed with: ", result)

        result = provider.register_node("mechatronics/dump", node_4)
        if result != datalayer.variant.Result.OK:
            print("bostroemc: Register count failed with: ", result)

        result = provider.register_node("mechatronics/done", node_5)
        if result != datalayer.variant.Result.OK:
            print("bostroemc: Register count failed with: ", result)        

        result= provider.start()
        if result != datalayer.variant.Result.OK:
            print("bostroemc: Starting Provider failed with: ", result)
            
        count=0
        while True:
            count=count+1
            if count > 7199:
                break
            time.sleep(1)
        
        result = provider.stop()
        print("bostroemc: Stopping provider loop...")

        if result != datalayer.variant.Result.OK:
            print("bostroemc: Stopping Provider failed with: ", result)

        result = provider.unregister_node("mechatronics/job_request")
        if result != datalayer.variant.Result.OK:
            print("bostroemc: Unregister Data Provider failed with: ", result)

        result = provider.unregister_node("mechatronics/pop")
        if result != datalayer.variant.Result.OK:
            print("bostroemc: Unregister Data Provider failed with: ", result)

def run():
    print("bostroemc: Simple Snap for ctrlX Datalayer Provider with Python")
    print("bostroemc: Connect to ctrlX CORE: ", connectionProvider)

    print("bostroemc: Create and start ctrlX Datalayer System")
    with datalayer.system.System("") as datalayer_system:
        datalayer_system.start(False)

        print("bostroemc: Creating provider...")
        with datalayer_system.factory().create_provider(connectionProvider) as provider:

            run_provider(provider)

        datalayer_system.stop(True)







        