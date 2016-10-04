import chunked_responses
from html.parser import HTMLParser
from urllib.parse import urljoin

class page_summary (HTMLParser):
            
    def __init__ (self, rootname,  onLink): # rootname must be canonical form.  Up to client to ensure this.
        super().__init__ ()
        self.rootname = rootname
        self.links = set ()
        self.error = ""
        self.onLink = onLink
        
        try:
            for chunk in chunked_responses.chunked_get (rootname, lambda resp: "/html" in resp.headers.get ("Content-Type", "").lower () ) :
                self.feed (chunk.decode('iso-8859-1') if isinstance (chunk, bytes) else chunk) # really nasty hack for when Responses guesses the charset wrong (or the page lies about it)
        except Exception as e:
            self.error = "ERROR: " + str(e); # if anything goes wrong, don't try to analyse the file.  Just leave it empty (and record the error)
        self.close()
        
    def getAttr (self, attrs, key): # extract an attribute, and canonicalise it
        for (k,v) in attrs :
            if (k == key): return urljoin (self.rootname, v)
        return self.rootname # <a> without href means placeholder link - IOW don't navigate anywhere.  The most sensible interpretation is a link-to-self

    @classmethod
    def setFlat (cls, isFlat): # must select this before starting to construct these things
        if isFlat:
            cls.SubAction = lambda self, url: self.onLink (url) # report everything for queueing through the tasklist
        else:
            cls.SubAction = lambda self, url: self.links.add (url) # lumpy: save everything in the page_summary.  (Only report the <a href>)
            
    def Action (self, url): 
        self.SubAction (url)
        return url
    
    def handle_starttag(self, tag, attrs):
        if (tag == "a"):
            self.onLink (self.Action (self.getAttr (attrs, "href"))) # onLink should be idempotent, so when isFlat, the extra onLink is safe
        elif (tag == "img") :
            self.Action (self.getAttr (attrs, "src"))
        elif (tag == "link") :
            self.Action (self.getAttr (attrs, "href"))
        elif (tag == "script") :
            self.Action (self.getAttr (attrs, "src"))
        elif (tag == "frame") :
            self.Action (self.getAttr (attrs, "src"))
        elif (tag == "iframe") :
            self.Action (self.getAttr (attrs, "src"))
        # Other tags, such as form; attributes, such as style; etc ...
        
    def __str__ (self) :
        rv = self.rootname + ":" + self.error
        for L in self.links: rv += "\n    " + L 
        return rv;




if __name__ == "__main__": # show the difference between flat and 'lumpy'
    print (page_summary ("http://www.webgineers.co.uk/", True, lambda q: print ("    ", q) ))
    print ("\n")
    
    print (page_summary ("http://www.webgineers.co.uk/", False, lambda q: print ("    ", q)))
    print ("\n")
