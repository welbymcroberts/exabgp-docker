#!/usr/bin/env python3

import sys
import requests
import argparse
from time import sleep


def log(prefix, message):
  sys.stderr.write("[{}] {}".format(prefix,message) + "\n")


def do_check(method="GET",
             url="http://127.0.0.1/",
             timeout=1.0,
             ssl_check=True,
             payload=None,
             username=None,
             password=None
             ):
  r = None

  log(url, "Starting request for {} with method {}. Timeout {}, Check SSL: {}".format(url, method, timeout, ssl_check))
  auth = None
  if username and password:
      auth = requests.auth.HTTPBasicAuth(username, password)
  try:
    # Make request
    if method.upper() == "GET":
      r = requests.get(url, timeout=timeout, verify=ssl_check, auth=auth)
    if method.upper() == "POST":
      r = requests.post(url, timeout=timeout, verify=ssl_check, data=payload, auth=auth)
    if method.upper() == "HEAD":
      r = requests.head(url, timeout=timeout, verify=ssl_check, auth=auth)
  except requests.exceptions.ConnectTimeout:
    log(url, "Request timeout")
  except requests.exceptions.RequestException:
    log(url, "Request failed with unknown exception")
  if isinstance(r, requests.Response):
    log(url, "Request completed with code {}".format(r.status_code))
  return r

def announce(ip):
  log("BGP", "Announcing {}".format(ip))
  sys.stdout.write("announce route {} next-hop self".format(ip) + '\n')

def withdraw(ip):
  log("BGP", "Withdrawing {}".format(ip))
  sys.stdout.write("withdraw route {} next-hop self".format(ip) + '\n')

if __name__ == '__main__':
  # Build out parser for commandline args
  parser = argparse.ArgumentParser()
  parser.add_argument("-i", "--ip", help="IP Address we will tell ExaBGP to announce")
  parser.add_argument("-u", "--url", help="URL which is to be tested")
  parser.add_argument("-m", "--method", help="HTTP method which is to be used for test")
  parser.add_argument("-s", "--status", help="Expected status for request. Defaults to 200", default=200, type=int)
  parser.add_argument("-t", "--timeout", help="Timeout for requests. Defaults to 2 seconds", default=2, type=float)
  parser.add_argument("-e", "--every", help="Time (in seconds) between checks. Defaults to 5 Seconds", default=5, type=float)
  parser.add_argument("-c", "--count", help="Number of times check passes or fails before announce/withdrawl. Defaults to 2.", default=2, type=int)
  parser.add_argument('-x', "--ssl-no-verify", help="Disable SSL checks", action="store_false")
  parser.add_argument('-p', "--payload", help="Payload if method is a POST")
  parser.add_argument('-U', "--username", help="Username")
  parser.add_argument('-P', "--password", help="Password")


  # Parse command line args
  args = parser.parse_args()

  counter=0
  # Start loop
  while True:
    # Do a request
    r = do_check(args.method, args.url, args.timeout, args.ssl_no_verify, args.payload, args.username, args.password)
    check_pass = False
    if isinstance(r, requests.Response):
      # is status the correct status
      if args.status == r.status_code:
        check_pass = True
        log(args.url, "Response code matches")
      else:
        log(args.url, "Response code does not match")

    if check_pass:
      # If counter is >1
      if counter >= 1:
        # Increase counter
        counter = counter+1
      else:
        # set to 1
        counter = 1
      # announce if the counter = count, dont renanoucne every check
      if counter == args.count:
        announce(args.ip)
    else:
      # If counter is >1
      if counter <= 0:
        counter = counter-1
      else:
        # set to 1
        counter = -1
      # announce if the counter = count, dont renanoucne every check
      if counter == args.count * -1:
        withdraw(args.ip)
    # Sleep until next check
    sleep(args.every)

