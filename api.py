#import ctypes
import csv
import gc
import json
import os
import pickle
import random
import sys
import time
from pathlib import Path
from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler



class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        path = self.path.replace("/", "").split("&")
 
        # basic response format checks
        if len(path[0][4:]) != 10 or not path[0][4:].isalnum() \
                                       or path[0][:4] != "sku=":
                self.wfile.write(b'Wrong API usage!')
                return None
        sku = path[0][4:]

        # if threshold is requested
        if len(path) == 2:
            if path[1][:2] != "k=":
                self.wfile.write(b'Wrong API usage!')
                return None
            k = path[1][2:]
            response = get_recommendations_filter(str(sku), float(k))
            self.wfile.write(json.dumps(response).encode("utf-8"))

        # if no threshold given within the URL
        elif len(path) == 1:
            response = get_recommendations_filter(str(sku))
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.wfile.write(b'Wrong API usage!')

def load_csv(fname="recommends.csv"):
    skus = defaultdict(list)
    with open(fname, newline='') as f:
        reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_NONE)
        for row in reader:
            skus[row[0]].append((row[1], float(row[2])))
    print("Loaded csv data as dict.")
    return skus

def get_recommendations_filter(sku, k=False):
    # if threshold is given
    if k:
        list_skus = skus[sku]
        res = list(filter(lambda x: x[1] >= k, list_skus))
        return res
    else:
        # no threshold given.
        res = skus[sku]
        return res



if __name__ == "__main__":
    skus = load_csv()
    #ip="35.224.184.222"
    ip="0.0.0.0"
    port=8000
    # ip = "localhost"
    # port = 80
    httpd = HTTPServer((ip, port), SimpleHTTPRequestHandler)
    print("Started serving API.")
    httpd.serve_forever()
