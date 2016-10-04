Jules May, jules@lunanlodge.co.uk, 07949 115253

# crawler
This is a project submitted for a programming test to BuildIt / Wipro, to crawl a website and report the pages and their links found there.  (Full spec by email, but not repeated here)

## Building and running

It's a console app: takes a command line, (no input), and sends output to stdout.

It's written in Python, and should be compatible with any V3.  Depends on `requests`, which is bundled with Python >= 3, but is installable on lower versions.

The project file is in Netbeans format, but you can load the source files into any Python IDE (including Idle), and run from there.  The startup file is `crawler.py`.

Execute the program as follows:

    crawler [toggles] [url]
where `toggles` is any of:

* `--t `_n_: set the number of worker threads (default 10)
* `-f` : selects flat output (that is, a list of every findable page and every reference in the site).  Default is "lumpy", which shows, for each findable page in the site, which urls it has linked to

`url` is the root of the website to be crawled.  Needs to be properly-qualified (i.e. `http://www.thing.com`, not just `thing.com`)

# Language
### Language of choice is Python

I selected Python because:

* It's designed for very quick hacking.  It doesn't clutter up the listings with lots of boilerplate, but instead is concise and allows the logic to show through;
* Python has (crude) html almost-parsing and http requests in-the-box.  Other platforms/languages would have required loading external libraries, which creates dependencies which probably aren't helpful in such a small project;
* if (in the code review) we decide to make some changes, Python will enable us to make the changes very quickly.

Downsides of Python are:

* It's only kinda-object-oriented.  'Pythonic' idioms are often anti-good.  Please don't interpret this as the best in OO style that I can do! :-)
* I've never programmed in Python before.  (Literally - this is my first time!) I might have missed something obvious.

### Other options
If this weren't a mashup, but was actually going into production code, then I wouldn't pick Python at all.  What I would pick would depend on specific requirements.

* If performance is key, and probably if this were an online service, then I'd pick C++.  It's fast, and the fine-grained memory control would be helpful.  I'd probably hand-code the html half-a-parser;
* If plasticity were important, then F# (if the shop were open to it), otherwise I'd go for Java or C#.  They're relatively easy to write in, and probably easier to maintain than C++.
* If it were definitely a service, then it could be done in php.  Nasty language, but lots of support (like Python), and dead easy to read.

## Unpacking the requirements
In principle, the task is easy: read a page, extract all the links, rinse-and-repeat.  But there's a few gotchas:

* html may be badly-formed.  We can't simply treat it as intolerantly as we could xml.  Need a very forgiving parser.
* Every img:src atribute should indicate an image of some kind (it's an error if not), but not every a:href attribute will indicate html.  Actually it can be anything.  So, we need to read the headers of a url in order to decide whether it's really a page or not.
* form:target attributes indicate pages that must be POSTed rather that GETted.  The enclosing form can give hints as to what should be posted, but that way lies a whole load of complexity and undecidability.   IMHO the only sensible approach is to fill in forms manually, or ignore them altogether.  This ignores them.  (NB, GETs with parameters are treated as unique pages.)
* Spec asks for a crawl of pages only in the origin domain.  To do that properly means:
  * we should check the CNAMEs of the domains to make sure apparently foreign links aren't just aliases of this one.
  * local urls may actually redirect to foreign domains.  Really, we should check the entire conversation on each page load. 

  This project doesn't address these, but there are todos in the code.

* Not all websites want to be crawled, and there are traps lying in wait for the unwary.  Two stand out:
  * A page can send an unending series of chunks.  Just consuming the page naively will generate an out-of-memory exception at best, and will stall the crawler at worst.
  * A page can contain a link to another page, which contains a link ... ad infinitum.  The crawler can chase these links down the rabbit hole, again, stalling or overflowing
* Some websites have a robots.txt file, showing which pages they want indexed (and, more to the point, which not).   But robots.txt doesn't declare dead-ends or black holes, it just suggests what should be publicised or not.  I've decided that for this task, we should ignore it: our purpose is to produce our own map (for reasons undisclosed). The robots.txt would be more useful when we come to process the pages we've discovered.

## Approach
### Multi-threaded
The most obvious character of this program is that it's multi-threaded.  Multi-threading is the easiest way to ameliorate the problems of trap pages (because even if one thread stalls, the others continue).  This is not a complete solution, of course, but with more tweaking it can be hardened as far as desired (for example, trapped threads could be killed-off by a watchdog).  It comprises:

* Main thread, which sets up the pipelines, and then waits for completion. (Completion is when the tasklist has drained, then the output queue has drained);
* A farm of worker threads, which read pages, emit their links, and then eventually emit the page summary to an output thread;
* The output thread, which prints pages to the console.

All the tasks are connected by thread-safe queues (which are the only IPC in the system):

* The worker threads are fed from a queue representing a tasklist (i.e. all the pages whose existence we know about, but are not yet processed).  When the tasklist empties, the work is done (which is why the main thread joins this one).
  * Note: this queue means that pages are evaluated breadth-first, which is our protection from rabbit-holes.  Rabbit holes can prevent the program from terminating, but won't stop the 'proper' site from being fully traversed.
  * Note, too: the input to the queue is filtered to weed out foreign links, and to disregard any page we already know about. (CNAME aliasing could be done here as well.)  All the urls must be in canonical form (the partial urls on the page must be canonicalised in the context of the page itself).
* The output thread is fed from a queue of page summaries.  Basically, the queue is there to accurately sequence the results: the output task is trivial.

### Scanning the pages
* Parsing is done chunk-by-chunk, and the AST is implied.  It is not necessary to load the entire page text, nor even to derive a complete DOM for the page. (This is how we protect against "infinite" pages.)
* The page summariser records only the lists necessary to produce its output.
* The page summaries, having been printed, are discarded immediately by the output thread.  (Other output process may choose to save them, but this approach doesn't demand they do.)
In fact, the only always-growing data in the system is the list of visited pages.  The net result is: no matter how big the website being scanned,  the memory requirements are modest, limited, and (with suitable protections in place) finite.  Overall, this approach will scale both up and out very easily.

Jules May, jules@lunanlodge.co.uk, 07949 115253

# crawler
This is a project submitted for a programming test to BuildIt / Wipro, to crawl a website and report the pages and their links found there.  (Full spec by email, but not repeated here)

## Building and running

The project is written in Python, and should be compatible with any V3.  Depends on `requests`, which is bundled with Python >= 3, but is installable on lower versions.

The project file is in Netbeans format, but you can load the source files into any Python IDE (including Idle), and run from there.  The startup file is `crawler.py`.

Execute the program as follows:

    crawler [toggles] [url]
where `toggles` is any of:

* `-t:`_n_: set the number of worker threads (default 10)

`url` is the root of the website to be crawled

## Language
### Language of choice is Python

I selected Python because:

* It's designed for very quick hacking.  It doesn't clutter up the listings with lots of boilerplate, but instead is concise and allows the logic to show through;
* Python has (crude) html almost-parsing and http requests in-the-box.  Other platforms/languages would have required loading external libraries, which creates dependencies which probably aren't helpful in such a small project;
* if (in the code review) we decide to make some changes, Python will enable us to make the changes very quickly.

Downsides of Python are:

* It's only kinda-object-oriented.  'Pythonic' idioms are often anti-good.  Please don't interpret this as the best in OO style that I can do! :-)
* I've never programmed in Python before.  (Literally - this is my first time!) I might have missed something obvious.

### Other options
If this weren't a mashup, but was actually going into production code, then I wouldn't pick Python at all.  What I would pick would depend on specific requirements.

* If performance is key, and probably if this were an online service, then I'd pick C++.  It's fast, and the fine-grained memory control would be helpful.  I'd probably hand-code the html half-a-parser;
* If plasticity were important, then F# (if the shop were open to it), otherwise I'd go for Java or C#.  They're relatively easy to write in, and probably easier to maintain than C++.
* If it were definitely a service, then it could be done in php.  Nasty language, but lots of support (like Python), and dead easy to read.

## Unpacking the requirements
In principle, the task is easy: read a page, extract all the links, rinse-and-repeat.  But there's a few gotchas:

* html may be badly-formed.  We can't simply treat it as intolerantly as we could xml.  Need a very forgiving parser.
* Every img:src atribute should indicate an image of some kind (it's an error if not), but not every a:href attribute will indicate html.  Actually it can be anything.  So, we need to read the headers of a url in order to decide whether it's really a page or not.
* form:target attributes indicate pages that must be POSTed rather that GETted.  The enclosing form can give hints as to what should be posted, but that way lies a whole load of complexity and undecidability.   IMHO the only sensible approach is to fill in forms manually, or ignore them altogether.  This ignores them.  (NB, GETs with parameters are treated as unique pages.)
* Spec asks for a crawl of pages only in the origin domain.  To do that properly means:
  * we should check the CNAMEs of the domains to make sure apparently foreign links aren't just aliases of this one.
  * local urls may actually redirect to foreign domains.  Really, we should check the entire conversation on each page load. 

  This project doesn't address these, but there are todos in the code.
* Spec asks for links to pages, and links to (e.g.) images.  But images can be referenced also in `style` attributes and css.  This doesn't follow those (although it's easy enough to add a style/css parser).  It also doesn't chase down progressively-loaded pages (such as Ajaxed pages).

* Not all websites want to be crawled, and there are traps lying in wait for the unwary.  Two stand out:
  * A page can send an unending series of chunks.  Just consuming the page naively will generate an out-of-memory exception at best, and will stall the crawler at worst.
  * A page can contain a link to another page, which contains a link ... ad infinitum.  The crawler can chase these links down the rabbit hole, again, stalling or overflowing
* Some websites have a robots.txt file, showing which pages they want indexed (and, more to the point, which not).   But robots.txt doesn't declare dead-ends or black holes, it just suggests what should be publicised or not.  I've decided that for this task, we should ignore it: our purpose is to produce our own map (for reasons undisclosed). The robots.txt would be more useful when we come to process the pages we've discovered.

## Approach
### Multi-threaded
The most obvious character of this program is that it's multi-threaded.  Multi-threading is the easiest way to ameliorate the problems of trap pages (because even if one thread stalls, the others continue).  This is not a complete solution, of course, but with more tweaking it can be hardened as far as desired (for example, trapped threads could be killed-off by a watchdog).  It comprises:

* Main thread, which sets up the pipelines, and then waits for completion. (Completion is when the tasklist has drained, then the output queue has drained);
* A farm of worker threads, which read pages, emit their links, and then eventually emit the page summary to an output thread;
* The output thread, which prints pages to the console.

All the tasks are connected by thread-safe queues (which are the only IPC in the system):

* The worker threads are fed from a queue representing a tasklist (i.e. all the pages whose existence we know about, but are not yet processed).  When the tasklist empties, the work is done (which is why the main thread joins this one).
  * Note: this queue means that pages are evaluated breadth-first, which is our protection from rabbit-holes.  Rabbit holes can prevent the program from terminating, but won't stop the 'proper' site from being fully traversed.
  * Note, too: the input to the queue is filtered to weed out foreign links, and to disregard any page we already know about. (CNAME aliasing could be done here as well.)  All the urls must be in canonical form (the partial urls on the page must be canonicalised in the context of the page itself).
* The output thread is fed from a queue of page summaries.  Basically, the queue is there to accurately sequence the results: the output task is trivial.

### Scanning the pages
* Parsing is done chunk-by-chunk, and the AST is implied.  It is not necessary to load the entire page text, nor even to derive a complete DOM for the page. (This is how we protect against "infinite" pages.)
* The page summariser records only the lists necessary to produce its output.
* The page summaries, having been printed, are discarded immediately by the output thread.  (Other output process may choose to save them, but this approach doesn't demand they do.)
In fact, the only always-growing data in the system is the list of visited pages.  The net result is: no matter how big the website being scanned,  the memory requirements are modest, limited, and (with suitable protections in place) finite.  Overall, this approach will scale both up and out very easily.


