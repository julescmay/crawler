# Tasklist is the queue containing all the pages known about but yet to be visited.
# It feeds the page_workers

import queue
import _thread
from urllib.parse import urlsplit

class TaskList (queue.Queue):
    def __init__ (self) :
        super().__init__ ()
        self.catalogue = set () # will be used to store the names of every page we've considered.  This is how we de-dup.
        self.a_lock = _thread.allocate_lock()
        
    def setRoot (self, url) : # TODO if this is ever used to re-root (say, to scan mutliple sites together) it will need locking.
        u_r_l = urlsplit (url)
        if u_r_l[0] == "" or u_r_l[1]=="" : raise ValueError (url + " is not a fully qualified url.  (I need something like http://www.there.com)")
        self.netloc = u_r_l[1]
        
    def put (self, url) : #perimieter security.  we'll only enqueue urls if they follow our rules.
        if len(self.catalogue) == 0: self.setRoot (url) # this is the first one.  Let's calibrate from here. 
                # Note: first one, so nothing in the workers, so nothing will interrupt us. Safe outside the lock
        with self.a_lock : # can be called asynchronously from any thread.  Need the following to be atomic.
            if url in self.catalogue : return # if we already know about it, don't ask again
            u_r_l = urlsplit (url)
            if not u_r_l[1] == self.netloc : return # if it's not part of the root domain, ignore it.  TODO check CNAME records
            # It's a new one.  Queue it up!
            self.catalogue.add (url)
            super().put(url)
    # TODO probably a#x and a#y should be the same page, so should disregard #'s. On the other hand, might be worth keeping to see which get referenced
    


# Don't really know how to unit-test the tasklist.  It really needs a bunch of multi-processing scaffolding around it to demonstrate it working.
# There's so little going on in the main program that we can use that as tasklist's integration test.