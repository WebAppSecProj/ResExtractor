#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import http.server
import socketserver
import Config
import os

class WebServerHelper:
    def __init__(self):
        pass

    # unfortunately, we can't manipulate SimpleHTTPRequestHandler to list files if there is an `index.html' or `index.htm' file in current folder.
    def startService(self):
        Handler = http.server.SimpleHTTPRequestHandler

        t = os.getcwd()
        web_dir = os.path.join(os.getcwd(), Config.Config["working_folder"])
        os.chdir(web_dir)

        self.httpd = socketserver.TCPServer(("", Config.Config["server_port"]), Handler)
        print("serving at port", Config.Config["server_port"])
        self.httpd.serve_forever()
        # TODO:: it's suspended here, use process instead??
        os.chdir(t)
        return

    def stopService(self):
        self.httpd.shutdown()
        return

def main():
    webServerHelper = WebServerHelper()
    webServerHelper.startService()

    return

if __name__ == "__main__":
    sys.exit(main())
