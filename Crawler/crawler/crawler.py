# This is the main program entry point.  
#  Build up the workers and queues, and then kick everything off.

from tasklist import TaskList
import queue
import threading
import page_summary
import argparse

tasklist = TaskList()
output_queue = queue.Queue()

def output_worker () : # where the results get printed
    while True:
        p = output_queue.get();
        print (p)
        output_queue.task_done ()
        
def page_worker () : # where the pages get summarised
    while True:
        url = tasklist.get()
        p = page_summary.page_summary (url,  lambda x: tasklist.put (x))
        output_queue.put (p)
        tasklist.task_done ()
    
    
# Execution starts here...

parser=argparse.ArgumentParser (description="Crawl a website")
parser.add_argument ('-f', action="store_true", default=False, dest="isFlat")
parser.add_argument ('--t', default=10, type=int, dest="nthreads")
parser.add_argument ('url', nargs=1)
args=vars (parser.parse_args())


t = threading.Thread (name="Output", target=output_worker); t.daemon=True; t.start()
for i in range (1,args['nthreads']): 
    t=threading.Thread (name="worker-" + str (i), target=page_worker); t.daemon=True; t.start()
# threads are daemons so they all stop automaictally when the program does.  (Otherwise it's really long-winded to shut everything down)
# Downside is: we stop being able to see them in the debugger.  Know they're running, bc the crawl is non-deterministic.

page_summary.page_summary.setFlat (args['isFlat']) # set the global behaviour of the page_summary objects

tasklist.put (args['url'][0]) # this triggers off the whole shudddering edifice 

tasklist.join() # wait for the tasklist to drain
output_queue.join() # and then for the output queue to drain
# Don't need to stop the threads.  They've gone quiescent: Just let them evaporate.
