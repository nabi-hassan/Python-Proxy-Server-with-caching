import socket
import signal
import threading
import ssl
import pickle # file format for saving cache dict
import atexit # used to save cache before program exit
import time, datetime
import re

BUFFER_LENGTH = 1048576 # buffer size = 2^20
cacheDict = {}

def saveDict(): # saves cache to cache.pkl when exiting the program
  with open('cache' + '.pkl', 'wb') as f:
    pickle.dump(cacheDict, f, pickle.HIGHEST_PROTOCOL)
    print ("cache saved")
    return 0

def readDict(): # reads the cache saved from last session in cache.pkl
    with open('cache' + '.pkl', 'rb') as f:
        cacheDict = pickle.load(f)

def exit_handler(): # on ctrl+C save cache
  saveDict()

def readBlocked(): # lists what urls have been blocked
  listBlocked = open("blocked.txt").read()
  print(listBlocked)

def writeToBlocked(block): # adds a new url to the list of blocked urls
  f = open("blocked.txt", "a")
  f.write(block + "\n")
  f.close

def removeBlocked(blocked): # unblocks a url
  lines = open("blocked.txt").read().splitlines()
  f = open("blocked.txt", "w")
  for line in lines:
    if (str(line) != (blocked)):
      f.write(str(line + "\n"))
  f.close



def inputLoop(): # prompts the user asking them if they would like to start the proxy, edit the blocked urls list or clear the cache
  while True:
    choice = int(input("Type 1 to start proxy server, 2 to block a url, 3 to unblock a url, 4 to list all blocked urls, 5 to clear cache: "))
    if choice == 1:
      port = int(input("Choose a port: "))
      server = Server(port)
    elif choice == 2:
      blockUrl = str(input("Type url to block: "))
      writeToBlocked(blockUrl)
      print("Url blocked")
    elif choice == 3:
      unblockUrl = str(input("Type url to unblock: "))
      removeBlocked(unblockUrl)
      print("Url unblocked")
    elif choice == 4:
      readBlocked()
    elif choice == 5:
    	cacheDict = {}
    	saveDict()
    else:
    	print("Command not recognised")

def main(): # begins by reading the saved cache and beginning user input prompt
  atexit.register(exit_handler) # set up cache save at exit
  readDict() # read cache from cache.pkl
  inputLoop() # begin IO


class Server: # Server class handles web socket connections
  def __init__(self, port):
    self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket creation
    self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.serverSocket.bind(('', port)) # bind localhost and port provided with our new socket
    self.serverSocket.listen(10) # queue up as many as 10 connect requests before refusing more
    while True:
      (webClient, proxy_address) = self.serverSocket.accept()
      threadListener = threading.Thread(target = self.requestReceived, args=(webClient, proxy_address)) # ready to create a new thread for any request made and run requestReceived
      threadListener.setDaemon(True)
      threadListener.start()
  def write_log(self, msg):
    with open("log/log.txt", "a+") as file:
      file.write(msg)
      file.write("\n")


  def isBlocked(self, blocked): # checks if a url is blocked
    target = str(blocked)
    Blocked = open("blocked.txt").read()
    Blocked = str(Blocked)
    if (target in Blocked):
      print(self.getTimeStampp() + "   Website Blacklisted")
      self.write_log(self.getTimeStampp() + "   Website Blacklisted")
      return True
    else:
      return False


  def getTimeStampp(self):
    return "[" + str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + "]"

  def getPort(self, request, url): # gets the port from a websocket request
    http_pos = url.find("://")
    if (http_pos==-1):
        temp = url
    else:
        temp = url[(http_pos+3):]
    port_pos = temp.find(":")
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)
    webserver = ""
    port = -1
    if (port_pos==-1 or webserver_pos < port_pos):

        port = 80
        webserver = temp[:webserver_pos]
    else:
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]
    return port

  def getUrl(self, request): # gets the url from a websocket request
    first_line = str(request).split('\n')[0]
    url = first_line.split(' ')[1]

    return url

  def getWebserver(self, request, url): # gets the webserver from a websocket request
    http_pos = url.find("://")
    if (http_pos==-1):
        temp = url
    else:
        temp = url[(http_pos+3):]
    port_pos = temp.find(":")
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)
    webserver = ""
    port = -1
    if (port_pos==-1 or webserver_pos < port_pos):

        port = 80
        webserver = temp[:webserver_pos]
    else:
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]
    return webserver

    
  def requestReceived(self, webClient, proxy_address):
    try:
      self.write_log(self.getTimeStampp() + "   \n\nStarting Server\n\n")
      request = webClient.recv(BUFFER_LENGTH) # receive request
      if (str(request).split('\n')[0] == "b''"): # check if request is empty and do nothing if it is
      	print("Empty request")
      	webClient.close()
      	return
      url = self.getUrl(request) # find url
      webserver = self.getWebserver(request, url) # find webserver
      port = self.getPort(request, url) # find port
      print("Request for website: " + url + " at Port: " + str(port))
      if (self.isBlocked(webserver)):
        print("Url is blocked")
        webClient.close() # if website is on the blocked list then close socket

      else:
        method = request.split(b" ")[0]
        if method == b"CONNECT":
          s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          try:
            start = time.time() # begin timing how long cache access takes
            self.write_log(self.getTimeStampp() + "  Cache Hit " + str(url) + "\n")
            data = cacheDict[request] # get request from cache
            reply = "HTTP/1.0 200 Connection established\r\n"
            reply += "\r\n"
            webClient.sendall(reply.encode())
            webClient.setblocking(0)
            s.setblocking(0)
            print("\n\nCache hit, fetching from cache\n\n")
            while True:
                try:
                    s.sendall(data)
                except socket.error as err:
                    pass

                try:
                    reply = s.recv(BUFFER_LENGTH)
                    cacheDict[request] = reply
                    webClient.sendall(reply)

                except socket.error as e:
                    pass
            end = time.time() # end timer
            timeElapsed = (end - start) * 1000
            print("Request for " + webserver + " handled from cache in " + str(timeElapsed) + "ms")
            webClient.close()

          except:
            try:
              # If successful, send 200 code response
              self.write_log(self.getTimeStampp() + " Not in Cache, showing from main server " + str(url) + "\n")
              s.connect((webserver, port))
              reply = "HTTP/1.0 200 Connection established\r\n"
              reply += "\r\n"
              webClient.sendall(reply.encode())
            except socket.error as err:
              pass

            webClient.setblocking(0)
            s.setblocking(0)
            print("  HTTPS Connection Established")
            print(" Not in Cache, showing from main server ")
            while True:
                try:
                    request = webClient.recv(BUFFER_LENGTH)
                    s.sendall(request)
                except socket.error as err:
                    pass

                try:
                    reply = s.recv(BUFFER_LENGTH)
                    cacheDict[request] = reply
                    webClient.sendall(reply)

                except socket.error as e:
                    pass
            end = time.time() # end timer
            timeElapsed = (end - start) * 1000
            print("Request completed in " + str(timeElapsed) + "ms")
            exit_handler()
            s.close()
            webClient.close()
        else:
          if (str(request).split('\n')[0] == "b''"): # check if request is empty and do nothing if it is
            print("Empty request")
            webClient.close()
            return
          url = self.getUrl(request) # find url
          webserver = self.getWebserver(request, url) # find webserver
          port = self.getPort(request, url) # find port
          print("Request for website: " + url + " at Port: " + str(port))
          if (request in cacheDict):
            print("Cache hit, fetching from cache")
            start = time.time() # begin timing how long cache access takes
            data = cacheDict[request] # get request from cache
            while 1:
              if (len(data) > 0):
                  webClient.send(data) # send data to browser
              else:
                  break
              break
            end = time.time() # end timer
            timeElapsed = (end - start) * 1000
            print("Request for " + webserver + " handled from cache in " + str(timeElapsed) + "ms") 
            webClient.close()
          else:
            start = time.time() # start timer to see how long request takes to process without cache access
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            s.connect((webserver, port))
            s.send(request) # send request to server
            while 1:
              data = s.recv(BUFFER_LENGTH) # receive data from server
              cacheDict[request] = data # save request in cache
              if (len(data) > 0):
                  webClient.send(data) # send data to browser
              else:
                  break
              break
            end = time.time() # end timer
            timeElapsed = (end - start) * 1000
            print("Request completed in " + str(timeElapsed) + "ms")
            exit_handler()
            s.close()
            webClient.close()

    except OSError:
      #print("Socket Error")
      pass
    except IOError:
      #print("Pipe Error")
      pass

if __name__== "__main__":
  main()
