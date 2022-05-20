# server.py
import http.server # Our http server handler for http requests
import socketserver # Establish the TCP Socket connections
import subprocess
import copy #reduce to j deepcopy if i remember
import sys

#dummy class to enable .kill() to be called on currentStream before it
#gets assigned to a real subprocess
class killBox():
    def kill():
        return

PORT = 8000
specifiedPaths = ("resources/icon.png")
errorMessagePage = None
#use cvlc to remove interface, vlc to keep
templatePlaylistArgs = ['vlc', '/home/pi/Public/server/resources/playlists/', '--sout=#transcode{vcodec=none,acodec=mp3,ab=128,channels=2,samplerate=44100,scodec=none}:duplicate{dst=http{dst=:8080/stream.mp3},dst=display}', '--sout-keep', '-L']
nextSongCommand = ['xdotool', 'key', 'alt+l', 'key', 'x']
prevSongCommand = ['xdotool', 'key', 'alt+l', 'key', 'v']
currentStream = killBox
temporarySubprocess = killBox

with open("/home/pi/Public/server/resources/error.html") as file:
    errorMessagePage = file.read()


def handleButtonLinks(callingObject):
    if "playlist." in callingObject.path:
        playPlaylist(callingObject)
    elif "nextSong" in callingObject.path:
        temporaryCommandlineCall(callingObject, nextSongCommand)
        eprint("fastForwarding")
    elif "prevSong" in callingObject.path:
        temporaryCommandlineCall(callingObject, prevSongCommand)
        eprint("prevSong")
        
def playPlaylist(callingObject):
    global currentStream
    print("current path:", callingObject.path)
    currentStream.kill()
    temp = copy.deepcopy(templatePlaylistArgs)
    temp[1] += callingObject.path[10:].replace("%20", " ") + ".xspf"
    print("Swapping to playlist", callingObject.path[10:])
    currentStream = subprocess.Popen(temp)
    callingObject.path = "/stream.html"
    
#for use in fastForward/backup commands
def temporaryCommandlineCall(callingObject, command):
    global temporarySubprocess
    temporarySubprocess.kill()
    temporarySubprocess = subprocess.Popen(command)
    callingObject.path = "/stream.html"  
    


class httpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/stream.html"
            
        #handle buttons
        handleButtonLinks(self)
            
        self.path = "/server" + self.path
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
 
    def send_error(self, code, message=None):
        
        handleButtonLinks(self)
            
        self.error_message_format = errorMessagePage
        http.server.SimpleHTTPRequestHandler.send_error(self, code, message)
        
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
        
handler = httpRequestHandler
 
with socketserver.TCPServer(("", PORT), handler) as httpd:
    print("Http Server Serving at port", PORT)
    httpd.serve_forever()
    
