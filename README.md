HTTP and HTTPS proxy server with caching(web proxy)
A proxy cache is a cache that is set up on an organisation's firewall or proxy server and is shared by all system/network users. When a system/network user accesses a web page, that page is temporarily stored in the proxy cache. Then, when a subsequent user requests the same web page, they access the copy in the proxy cache, rather than having the web page sent again from the originating server.

Getting Started
Proxy server in Python that can handle HTTP/HTTPS requests , Caching, Websites and IP blocking. It also provides logging for debugging purposes. The code does not use any external networking module. It is written using the 'socket' module which comes pre-installed with python.
Project Description: 
	Web proxy caching stores copies of frequently accessed Web objects (such as web pages) close to users and serves this information to them. Internet users get their information faster, and Internet bandwidth is freed for other tasks.
	At the very simplest level, a cache server is responsible for serving items that have already been requested from the main server. Doing this gives the main server a break from having to respond to every request, and the workload can be shared by the cache server.


Usage
For Firefox:
    1. Goto Options
    2. Type proxy in the search bar and click on Settings.. for the Network Proxy tab
    3. Select Manual Proxy Configuration and enter localhost in HTTP Proxy and enter the port number which you entered when running the proxy program in the Port tab ( in my case I entered 55555 ).
    4. Check Use this proxy server for all protocols
For Chrome:
    1. Goto your windows settings.
    2. Click on Network and Internet.
    3. On the left hand menu click on Proxy.
    4. Turn on the use proxy server option.
    5. Then type 127.0.0.1 in the address tab and the port number which you entered when running the proxy program.
    6. Then click save and exit.


Built With
Python 3.7


Used Libraries
    • socket
    • threading
    • ssl
    • pickle  (file format for saving cache dict)
    • atexit (used to save cache before program exit)
    • time, datetime
    • re
