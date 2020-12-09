#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import http.server
import socketserver
import Config
import os

class WebServerHelper:
    def __init__(self, root_path):
        self.web_server_root = root_path


    # return the ip and port
    def startService(self):
        Handler = http.server.SimpleHTTPRequestHandler

        t = os.getcwd()
        web_dir = os.path.join(os.getcwd(), self.web_server_root)
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
    # webServerHelper = WebServerHelper("../libs/modules/DCloud/./working_folder/103a97f1a8cdbe9a4f80187279f3b78f9e0e7acd")
    webServerHelper = WebServerHelper("../libs/modules/APICloud/./working_folder/0c8b013e173768eabf68fead38f4a1c17b949d1a")
    webServerHelper.startService()

    return

if __name__ == "__main__":
    sys.exit(main())
