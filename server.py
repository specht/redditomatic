#!/usr/bin/env python
import time
import BaseHTTPServer


HOST_NAME = '192.168.11.6'
PORT_NUMBER = 5555


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        contents = ''
        with open('test.pbm') as f:
            contents = f.read()
            
        height = 576
        
        y0 = 0

        # send image in 384x128 pixel spans
        while True:
            y1 = y0 + 128
            if y1 > height - 1:
                y1 = height - 1
            partheight = y1 - y0
            
            s.wfile.write(chr(18))
            s.wfile.write(chr(42))
            s.wfile.write(chr(partheight))
            s.wfile.write(chr(384/8))
            for i in range(partheight):
                s.wfile.write(contents[(50 + 48 * (i + y0)):(50 + 48 * (i + y0) + 48)])
                
            y0 = y1 + 1
            if y0 >= height:
                break
        s.wfile.flush()
        s.wfile.close()

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)