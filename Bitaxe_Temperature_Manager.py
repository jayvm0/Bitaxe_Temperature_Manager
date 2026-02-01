### bitaxe_mngr.py

from concurrent.futures import ThreadPoolExecutor
import json
import requests
import time
import traceback

minerIps = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]

chk_interval = 10

crit_asictemp = 73
crit_vrtemp = 78

def_freq = 525
def_corevolt = 1000

min_freq = 400
max_freq = 500

min_corevolt = 1000
max_corevolt = 1150

max_asictemp = 66
max_vrtemp = 75
max_watt = 24
max_error = 1

################################################################

def printError(e) :
  frame_summary = traceback.extract_tb(e.__traceback__)[-1]
  print(f"Exception: {e}:{frame_summary.filename}:{frame_summary.lineno}")

################################################################

def initialize(miner) :
  url_id = "http://" + miner + "/api/system/identify"

  try :
    response = requests.post(url_id, timeout=5)
  except requests.RequestException as e :
    printError(e)
  else :
    if response.status_code == 200 :
      try:
        url_patch = "http://" + miner + "/api/system"
        mnr_volt = def_corevolt
        mnr_freq = def_freq
        data = {"frequency": mnr_freq, "coreVoltage": mnr_volt}
        headers = {"Content-Type": "application/json"}
        requests.Response = requests.patch(url_patch, json=data, headers=headers, timeout=5)
      except requests.RequestException as e:
        printError(e)

################################################################

def initializeMiners(miners) :
  with ThreadPoolExecutor(max_workers = len(miners)) as executor:
    for miner in miners :
      executor.submit(initialize, miner)

################################################################

def manageMiner(miner):
  url = "http://" + miner + "/api/system/info"
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
    cur_watt = miner_info['power']

    delta_volt = 0
    delta_freq = 0

    if cur_asictemp > max_asictemp or cur_vrtemp > max_vrtemp or cur_watt > max_watt: # asic temp is hot
      if cur_corevolt > min_corevolt :
        if cur_asictemp > crit_asictemp or cur_vrtemp > crit_vrtemp :
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
      url = "http://" + miner + "/api/system"
      data = {"frequency": mnr_freq, "coreVoltage": mnr_volt}
      headers = {"Content-Type": "application/json"}

      print("=============================================")
      print(f"Power {cur_watt} - {max_watt}")
      print(f"Err Rate {cur_error} - {max_error}")
      print(f"Frequency {cur_freq} - {max_freq}")
      print(f"Core Voltage {cur_corevolt} - {max_corevolt}")
      print(f"Asic Temp {cur_asictemp} - {max_asictemp}")
      print(f"New Frequency {mnr_freq}")
      print(f"New Core Voltage {mnr_volt}")
      try:
        response = requests.patch(url, json=data, headers=headers, timeout=5)
      except requests.RequestException as e:
        printError(e)
        return False

################################################################

initializeMiners(minerIps)

while True:
  with ThreadPoolExecutor(max_workers = len(minerIps)) as executor:

    for minerIp in minerIps :
      executor.submit(manageMiner, minerIp)

  time.sleep(chk_interval)
