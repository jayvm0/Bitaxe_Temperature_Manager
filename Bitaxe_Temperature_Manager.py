### bitaxe_mngr.py

from concurrent.futures import ThreadPoolExecutor
import json
import requests
import time
import traceback
import sys

pollInterval = 10
runManager = False
farm = []

################################################################

def printError(e) :
  frame_summary = traceback.extract_tb(e.__traceback__)[-1]
  print(f"Exception: {e}:{frame_summary.filename}:{frame_summary.lineno}")

################################################################

def readConfig() :
  global runManager
  global pollInterval
  global farm

  if len(sys.argv) > 1 :
    configFile = sys.argv[1]
  else :
    configFile = 'config.json'

  try :
    with open(configFile, 'r') as file:
      config = json.load(file)
  except FileNotFoundError as e :
    printError(e)
    return(False)
  else :
    runManager = config["run_manager"]
    pollInterval = config["poll_interval"]
    farm = config["farm"]
    return(True)

################################################################

def initializeMiner(miner, fleetParam) :
  defFreq = fleetParam["def_freq"]
  defCoreVolt = fleetParam["def_corevolt"]
  url = "http://" + miner + "/api/system"
  mnr_volt = defCoreVolt
  mnr_freq = defFreq
  data = {"frequency": mnr_freq, "coreVoltage": mnr_volt}
  headers = {"Content-Type": "application/json"}

  try :
    response = requests.patch(url, json=data, headers=headers, timeout=5)
  except requests.RequestException as e :
    printError(e)
    return False
  else :
    status_code = response.status_code
    if status_code == 200 :
      return True
    else :
      return False

################################################################

def manageMiner(miner, fleetParam) :
  fleetName = fleetParam["name"]
  critAsicTemp = fleetParam["crit_asictemp"]
  critVRTemp = fleetParam["crit_vrtemp"]
  defFreq = fleetParam["def_freq"]
  defCoreVolt = fleetParam["def_corevolt"]
  minFreq = fleetParam["min_freq"]
  maxFreq = fleetParam["max_freq"]
  minCoreVolt = fleetParam["min_corevolt"]
  maxCoreVolt = fleetParam["max_corevolt"]
  maxAsicTemp = fleetParam["max_asictemp"]
  maxVRTemp = fleetParam["max_vrtemp"]
  maxWatt = fleetParam["max_watt"]
  maxError = fleetParam["max_error"]

  url = "http://" + miner + "/api/system/info"
  try :
    response = requests.get(url, timeout=5)
  except requests.RequestException as e :
    printError(e)
    return False
  else :
    statusCode = response.status_code
    if statusCode == 200 :
      try :
        minerInfo = response.json()
      except requests.RequestException as e :
        printError(e)
        return False
      else :
        curVRTemp = minerInfo['vrTemp']
        curAsicTemp = minerInfo['temp']
        curError = minerInfo['errorPercentage']
        curFreq = minerInfo['frequency']
        curCoreVolt = minerInfo['coreVoltage']
        curWatt = minerInfo['power']

        deltaVolt = 0
        deltaFreq = 0

        if curAsicTemp > maxAsicTemp or curVRTemp > maxVRTemp or curWatt > maxWatt : # asic temp is hot
          if curCoreVolt > minCoreVolt :
            if curAsicTemp > critAsicTemp or curVRTemp > critVRTemp :
              if curCoreVolt > defCoreVolt :
                deltaVolt = defCoreVolt - curCoreVolt
              else :
                deltaVolt = minCoreVolt - curCoreVolt
              if curFreq > defFreq :
                deltaFreq = defFreq - curFreq
              else:
                deltaFreq = minFreq - curFreq
            else :
              deltaVolt = -1
              if (curFreq % 4) == 0 :
                deltaFreq = -1
          else :
            if curFreq > minFreq :
              deltaFreq = -1
        else :
          if curError > maxError :
            if curCoreVolt < maxCoreVolt :
              deltaVolt = 1
            if curFreq < maxFreq :
              deltaFreq = 1

        if deltaVolt != 0 or deltaFreq != 0 :
          mnrVolt = curCoreVolt + deltaVolt
          mnrFreq = curFreq + deltaFreq
          url = "http://" + miner + "/api/system"
          data = {"frequency": mnrFreq, "coreVoltage": mnrVolt}
          headers = {"Content-Type": "application/json"}

          print("=============================================")
          print(f"Fleet: {fleetName}")
          print(f"Miner: {miner}")
          print(f"Power {curWatt} [{maxWatt}]")
          print(f"Err Rate {curError} [{maxError}]")
          print(f"Frequency {curFreq} [{maxFreq}]")
          print(f"Core Voltage {curCoreVolt} [{maxCoreVolt}]")
          print(f"Asic Temp {curAsicTemp} [{maxAsicTemp}]")
          print(f"New Frequency {mnrFreq}")
          print(f"New Core Voltage {mnrVolt}")

          try :
            response = requests.patch(url, json=data, headers=headers, timeout=5)
          except requests.RequestException as e :
            printError(e)
            return False
          else :
            status_code = response.status_code
            if status_code == 200 :
              return True
            else :
              return False

################################################################

if readConfig() :
  if runManager :
    for fleet in farm :
      fleetMiners = fleet["miners"]
      with ThreadPoolExecutor(max_workers = len(fleetMiners)) as executor:
        for miner in fleetMiners :
            executor.submit(initializeMiner, miner, fleet)

    time.sleep(pollInterval)

  while runManager :
    for fleet in farm :
      fleetMiners = fleet["miners"]
      with ThreadPoolExecutor(max_workers = len(fleetMiners)) as executor :
        for miner in fleetMiners :
          executor.submit(manageMiner, miner, fleet)

    time.sleep(pollInterval)
    readConfig()

  print("End")
  sys.exit(0)
else :
  sys.exit(1)
