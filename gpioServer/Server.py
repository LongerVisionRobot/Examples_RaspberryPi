
################################################################################
#                                                                              #
#                                                                              #
#           IMPORTANT: READ BEFORE DOWNLOADING, COPYING AND USING.             #
#                                                                              #
#                                                                              #
#      Copyright [2017] [ShenZhen Longer Vision Technology], Licensed under    #
#      ******** GNU General Public License, version 3.0 (GPL-3.0) ********     #
#      You are allowed to use this file, modify it, redistribute it, etc.      #
#      You are NOT allowed to use this file WITHOUT keeping the License.       #
#                                                                              #
#      Longer Vision Technology is a startup located in Chinese Silicon Valley #
#      NanShan, ShenZhen, China, (http://www.longervision.cn), which provides  #
#      the total solution to the area of Machine Vision & Computer Vision.     #
#      The founder Mr. Pei JIA has been advocating Open Source Software (OSS)  #
#      for over 12 years ever since he started his PhD's research in England.  #
#                                                                              #
#      Longer Vision Blog is Longer Vision Technology's blog hosted on github  #
#      (http://longervision.github.io). Besides the published articles, a lot  #
#      more source code can be found at the organization's source code pool:   #
#      (https://github.com/LongerVision/OpenCV_Examples).                      #
#                                                                              #
#      For those who are interested in our blogs and source code, please do    #
#      NOT hesitate to comment on our blogs. Whenever you find any issue,      #
#      please do NOT hesitate to fire an issue on github. We'll try to reply   #
#      promptly.                                                               #
#                                                                              #
#                                                                              #
# Version:          0.0.1                                                      #
# Author:           Zhuang Bonan                                               #
# Contact:          zhuangbonan@longervision.com                               #
# URL:              http://www.longervision.cn                                 #
# Create Date:      2017-04-10                                                 #
################################################################################

import re
import sysfrom http.server import HTTPServer, BaseHTTPRequestHandler

import os
import time
from lxml.builder import E
from lxml import etree
import RPi.GPIO as GPIO
my_not = lambda x : not x

class PinControler():
    gpioPins = [7,11,12,13,15,16,18,22,29,31,32,33,35,36,37,38,40]
    gpioNameDict = {
                    "GPIO.0": 11,
                    "GPIO.1": 12,
                    "GPIO.2": 13,
                    "GPIO.3": 15,
                    "GPIO.4": 16,
                    "GPIO.5": 18,
                    "GPIO.6": 22,
                    "GPIO.7": 7,
                    "GPIO.21": 29,
                    "GPIO.22": 31,
                    "GPIO.23": 33,
                    "GPIO.24": 34,
                    "GPIO.25": 17,
                    "GPIO.26": 32,
                    "GPIO.27": 36,
                    "GPIO.28": 38,
                    "GPIO.29": 40,
                    }
    pinStates = {}
    cmds = {}
    cmdSpliter = re.compile('([^&\|\^\=\(\)|\?\!]+)')
    GPIO.setmode(GPIO.BOARD)
    for i in gpioPins:
        pinStates[i] = 0
        GPIO.setup(i,GPIO.OUT)
        GPIO.output(i,0)
    for i in gpioPins:
        pinStates[i] = {"state":0,"dir":0}

    def change_pin_state(self, pin):
        if pin not in self.pinStates:
            return -1
        elif self.pinStates[pin]["dir"]:
            return self.pinStates[pin]
        else:
            self.pinStates[pin]["state"] = (self.pinStates[pin]["state"] + 1) % 2
            GPIO.output(pin,self.pinStates[pin]["state"])
            return self.pinStates[pin]

    def change_pin_dir(self,pin):
        if pin not in self.pinStates:
            return -1
        else:
            self.pinStates[pin]["dir"] = (self.pinStates[pin]["dir"] + 1) % 2
            if self.pinStates[pin]["dir"]:
                GPIO.setup(pin,GPIO.IN)
            else:
                GPIO.setup(pin,GPIO.OUT)
                GPIO.output(pin,0)
            self.pinStates[pin]["state"] = 0
            if pin in self.cmds:
                del(self.cmds[pin])

            for key in list(self.cmds.keys()):
                for p in range(2,len(self.cmds[key]['compiled']),2):
                    if self.cmds[key]['compiled'][p] == pin:
                        del(self.cmds[key])
                        break
            return self.pinStates[pin]

    def run_cmd(self,cmd):
        code = cmd.copy()
        for i in range(2,len(cmd),2):
            code[i] = str(self.pinStates[cmd[i]]["state"])
        try:
            print("".join(code[1:]))
            self.pinStates[code[0]]["state"] = eval("".join(code[1:])) and 1 or 0
            GPIO.output(code[0],self.pinStates[code[0]]["state"])
            print("OK")
            return 1
        except:
            print("Failed")
            return 0

    def add_cmd(self,cmd):
        pins = self.cmdSpliter.split(cmd)
        #pins[0] = pins[0].split("?")[1]
        pins = pins[3:]
        print(pins)
        size = len(pins)
        if size < 3 and pins[0] in self.gpioNameDict:
            print(self.gpioNameDict[pins[0]])
            print(self.cmds)
            if self.gpioNameDict[pins[0]] in self.cmds:
                del(self.cmds[self.gpioNameDict[pins[0]]])
                print(self.cmds)
                return "Success"

        if size < 3 or size % 2 == 1:
            return "syntactic error"

        if pins[0] not in self.gpioNameDict:
            return pins[0]+" is not a GPIO pin name"
        elif self.pinStates[self.gpioNameDict[pins[0]]]["dir"]:
            return pins[0] + " is not a output pin"
        else:
            #pins[0] = str(self.pinStates[self.gpioNameDict[pins[0]]]["state"])
            pins[0] = self.gpioNameDict[pins[0]]
            temp = pins[1].split("!")
            if len(temp) > 1 and temp[-1] is "":
                temp[1] = temp[1]+"("
                pins[3] = ")" + pins[3]
            pins[1] = " my_not ".join(temp)
            pins[1] = "".join(pins[1].split("="))

        for i in range(2,size,2):
            if pins[i] not in self.gpioNameDict:
                return pins[i] + " is not a GPIO pin name"
            elif not self.pinStates[self.gpioNameDict[pins[i]]]["dir"]:
                return pins[i] + " is not a input pin"
            else:
                #pins[i] = str(self.pinStates[self.gpioNameDict[pins[i]]]["state"])
                pins[i] = self.gpioNameDict[pins[i]]
                if not pins[i+1] == '':
                    temp = pins[i+1].split("!")
                    print(temp)
                    if len(temp) > 1 and temp[-1] is "":
                        temp[1] = temp[1]+"("
                        pins[i+3] = ")" + pins[i+3]
                    pins[i+1] = " my_not ".join(temp)
        print(pins)
        if self.run_cmd(pins):
            self.cmds[pins[0]] = {"source":cmd.split('?')[1],"compiled":pins}
            return "Success"
        else:
            return "syntactic error"

    def update_pins_state(self):
        for key in self.pinStates:
            if self.pinStates[key]["dir"]:
                self.pinStates[key]["state"] = GPIO.input(key) and 1 or 0
        for key in self.cmds:
            print(self.cmds[key])
            self.run_cmd(self.cmds[key]["compiled"])

    def get_pins_state(self):
        self.update_pins_state()
        for key in self.pinStates:
            if key in self.cmds:
                self.pinStates[key]["cmd"] = self.cmds[key]["source"]
            else:
                self.pinStates[key]["cmd"] = ""
        return self.pinStates


class ServerHttpHandler(BaseHTTPRequestHandler):
    pinControler = PinControler()
    def __init__(self,request, client_address, server):
        self.GET_functions = {"status": self.get_status}
        self.POST_functions = {"pinChange": self.post_pin_change,
                               "pinChangeDir":self.post_pin_change_dir,
                               "sendCmd":self.post_cmd_add}
        self.paramsFinder = re.compile('[\&|\?]([^=&]+)\=*([^&#]*)')
        self.filePathFinder = re.compile('[\/]([^?]+)[\?]*')
        BaseHTTPRequestHandler.__init__(self,request, client_address, server)

    def get_status(self,path):
        params = self.paramsFinder.findall(self.path)
        print(path)
        print(params)
        text = ""
        for pair in params:
            text = text + " ".join(pair) + ","

        self.send_response(200)
        self.send_header("Content-type", "text/xml")
        self.end_headers()
        status = self.pinControler.get_pins_state();
        root = E.results()
        for key in status:
            state = status[key]['state'] and "On" or "Off"
            dir = status[key]['dir'] and "In" or "Out"
            cmd = status[key]["cmd"]
            root.append(E.Pin(id=str(key), state=state, dir=dir, cmd=cmd))

        self.wfile.write(etree.tostring(root))

    def post_pin_change(self,path):
        params = self.paramsFinder.findall(self.path)
        print(path)
        print(params)
        for pair in params:
            if pair[0] == "pin":
                pin = int(pair[1])
                self.send_response(200)
                self.send_header("Content-type", "text/xml")
                self.end_headers()
                res = self.pinControler.change_pin_state(pin)
                if res == -1:
                    state = "Error"
                    dir = "Error"
                else:
                    state = res['state'] and "On" or "Off"
                    dir = res['dir'] and "In" or "Out"
                self.wfile.write(etree.tostring(
                    E.results(
                        E.Pin(id=pair[1],state=state,dir=dir))))

    def post_pin_change_dir(self,path):
        params = self.paramsFinder.findall(self.path)
        print(path)
        print(params)
        for pair in params:
            if pair[0] == "pin":
                pin = int(pair[1])
                self.send_response(200)
                self.send_header("Content-type", "text/xml")
                self.end_headers()
                res = self.pinControler.change_pin_dir(pin)
                if res == -1:
                    state = "Error"
                    dir = "Error"
                else:
                    state = res['state'] and "On" or "Off"
                    dir = res['dir'] and "In" or "Out"
                self.wfile.write(etree.tostring(
                    E.results(
                        E.Pin(id=pair[1],state=state,dir=dir))))

    def post_cmd_add(self,path):
        res = self.pinControler.add_cmd(path)
        self.send_response(200)
        self.send_header("Content-type", "text/xml")
        self.end_headers()
        self.wfile.write(bytes(res,"utf8"))

    def do_GET(self):
        print(self.path)
        path = self.filePathFinder.findall(self.path)
        params = self.paramsFinder.findall(self.path)
        print(path)
        print(params)
        if len(path) > 0:
            if os.path.exists(path[0]):
                self.send_response(200)
                fileType = path[0].split(".")
                if(fileType[1] == "html"):
                    self.send_header("Content-type", "text/html")
                elif(fileType[1] == "css"):
                    self.send_header("Content-type", "text/css")
                else:
                    self.send_header("Content-type", "text/plain")
                self.end_headers()
                htmlFile = open(path[0],"rb")
                self.wfile.write(htmlFile.read())
                htmlFile.close()
            elif path[0] in self.GET_functions:
                self.GET_functions[path[0]](params)
            else:
                self.send_response(404)
                self.send_header("Content-type","text/plain")
                self.end_headers()
                self.wfile.write(b"File Not Exists")
        else:
            self.send_response(200)
            self.send_header("Content-type","text/html")
            self.end_headers()
            indexFile = open("index.html","rb")
            self.wfile.write(indexFile.read())

    def do_POST(self):
        print(self.path)
        path = self.filePathFinder.findall(self.path)

        if len(path) > 0:
            if os.path.exists(path[0]):
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                htmlFile = open(path[0], "rb")
                self.wfile.write(htmlFile.read())
                htmlFile.close()
            elif path[0] in self.POST_functions:
                self.POST_functions[path[0]](self.path)
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"File Not Exists")
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            indexFile = open("index.html", "rb")
            self.wfile.write(indexFile.read())


if len(sys.argv) != 3:
    print("Usage: python3 Server.py SERVER_IP SERVER_PORT")
else:
    handler = ServerHttpHandler
    http_server = HTTPServer((sys.argv[1], int(sys.argv[2])), handler)
    http_server.serve_forever()
