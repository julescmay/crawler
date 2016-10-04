# A function which uses the requests library to deliver a function which enumerates over chunks.
# Alternative approach - enumerate over lines of source (which would give us at least chunks, and possibly finer-grained still)

import requests
import sys

def chunked_get(url, filter = lambda sess : True): # if the filter says False, the page won't be scanned
    sess = requests.sessions.Session()
    sess.verify = False
    sess.prefetch = False
    resp = sess.get(url, stream=True)
    if not filter (resp): # if filter says false, don't read the content
        pass
    elif resp.headers.get ("Transfer-Encoding", "").lower() == "chunked": # default of "" is to make sure lower is defined
        for chunk in resp.iter_content(None):
            yield(chunk)
    else:
        yield resp.text
    resp.close()




if __name__ == '__main__': # tests, and demonstration of how to use it
    chunk_count = 0;
    for chunk in chunked_get ("http://jigsaw.w3.org/HTTP/ChunkedScript") : # this is an online test page that returns 9 chunks.
    #for chunk in chunked_get ("http://jigsaw.w3.org/HTTP/TE/foo.txt") : # this is an online test page that returns 1 (very large) chunk. Should print OK but fail the test
        chunk_count += 1
    if (chunk_count != 9):
        raise AssertionError ("Incorrect number of chunks returned: " + str (chunk_count))
    print ("OK")
    
    chunk_count = 0;
    for chunk in chunked_get ("http://jigsaw.w3.org/HTTP/ChunkedScript", lambda resp: "/html"  in resp.headers.get ("Content-Type", "").lower ()) : # but the page is /text, not /html.
        chunk_count += 1
    if (chunk_count != 0):
        raise AssertionError ("Incorrect number of chunks returned: " + str (chunk_count))
    print ("OK")
    
    chunk_count = 0;
    for chunk in chunked_get ("http://www.google.com", lambda resp: "/html"  in resp.headers.get ("Content-Type", "").lower ()) : # here's an /html page, in one chunk
        chunk_count += 1
    if (chunk_count != 1):
        raise AssertionError ("Incorrect number of chunks returned: " + str (chunk_count))
    print ("OK")
    sys.exit(0)