### bitaxe_mngr.py

import requests
import json
import time
import traceback

miner_ip = "192.168.1.1"

chk_interval = 10

crit_temp = 73
crit_vrtemp = 78

def_freq = 500
def_corevolt = 1000

min_freq = 400
max_freq = 500

min_corevolt = 1000
max_corevolt = 1150

max_asictemp = 66
max_vrtemp = 75
max_error = 2

################################################################
def printError(e) :
  frame_summary = traceback.extract_tb(e.__traceback__)[-1]
  print(f"Exception: {e}:{frame_summary.filename}:{frame_summary.lineno}")

def manage_temp():
  url = "http://" + miner_ip + "/api/system/info"
  try:
    response = requests.get(url, timeout=5)
  except requests.RequestException as e:
    printError(e)
    return False

  status_code = response.status_code
  if status_code == 200 :
    try :
      miner_info = response.json()
    except requests.RequestException as e:
      printError(e)
      return False

    cur_vrtemp = miner_info['vrTemp']
    cur_asictemp = miner_info['temp']
    cur_error = miner_info['errorPercentage']
    cur_freq = miner_info['frequency']
    cur_corevolt = miner_info['coreVoltage']

    delta_volt = 0
    delta_freq = 0

    if cur_asictemp > max_asictemp or cur_vrtemp > max_vrtemp : # asic temp is hot
      if cur_corevolt > min_corevolt :
        if cur_asictemp > crit_temp :
          delta_volt = def_corevolt - cur_corevolt
          delta_freq = def_freq - cur_freq
        else :
          delta_volt = -1
      else :
        if cur_freq > min_freq :
          delta_freq = -1
    else :
      if cur_error > max_error :
        if cur_corevolt < max_corevolt :
          delta_volt = 1
        if cur_freq < max_freq :
          delta_freq = 1
          
    if delta_volt != 0 or delta_freq != 0:
      mnr_volt = cur_corevolt + delta_volt
      mnr_freq = cur_freq + delta_freq
      url = "http://" + miner_ip + "/api/system"
      data = {"frequency": mnr_freq, "coreVoltage": mnr_volt}
      print("error rate: ", cur_error, " cur_corevolt: ", cur_corevolt)
      print("new asic frequency: ", mnr_freq, " new core voltage: ", mnr_volt)
      try:
        response = requests.patch(url, json=data, timeout=5)
      except requests.RequestException as e:
        printError(e)
        return False

################################################################

url = "http://" + miner_ip + "/api/system/identify"

try:
  response = requests.post(url, timeout=5)
except requests.RequestException as e:
  printError(e)

mnr_volt = def_corevolt
mnr_freq = def_freq

url = "http://" + miner_ip + "/api/system"
data = {"frequency": mnr_freq, "coreVoltage": mnr_volt}
try:
  response = requests.patch(url, json=data, timeout=5)
except requests.RequestException as e:
  printError(e)

while True:

  manage_temp()
  time.sleep(chk_interval)
