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
pollIter = 1

################################################################

def printError(e) :
  frame_summary = traceback.extract_tb(e.__traceback__)[-1]
  print(f"Exception: {e}:{frame_summary.filename}:{frame_summary.lineno}")

################################################################

def isNumber(var) :
  return(type(var) in [int, float])

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
    if not isinstance(runManager, bool) :
      runManager = False

    pollInterval = config["poll_interval"]
    if not isNumber(pollInterval) :
      return(False)
    else :
      if pollInterval < 5 :
        pollInterval = 5

    farm = config["farm"]
    if not isinstance(farm, list) :
      return(False)
    else :
      return(True)

################################################################

def initializeMiner(miner, fleetParam) :
  defFreq = fleetParam["def_freq"]
  if not isNumber(defFreq) :
    raise(ValueError)

  defCoreVolt = fleetParam["def_corevolt"]
  if not isNumber(defCoreVolt) :
    raise(ValueError)

  url = "http://" + miner + "/api/system"
  mnr_volt = defCoreVolt
  mnr_freq = defFreq
  data = {"frequency": mnr_freq, "coreVoltage": mnr_volt}
  headers = {"Content-Type": "application/json"}

  try :
    response = requests.patch(url, json=data, headers=headers, timeout=2)
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

def setToMinimum(miner, fleetParam) :
  # minFreq = fleetParam["min_freq"]
  # if not isNumber(minFreq) :
  #   raise(ValueError)

  # minCoreVolt = fleetParam["min_corevolt"]
  # if not isNumber(minCoreVolt) :
  #   raise(ValueError)

  # url = "http://" + miner + "/api/system"
  # mnr_volt = minCoreVolt
  # mnr_freq = minFreq
  # data = {"frequency": mnr_freq, "coreVoltage": mnr_volt}
  # headers = {"Content-Type": "application/json"}

  # try :
  #   response = requests.patch(url, json=data, headers=headers, timeout=2)
  # except requests.RequestException as e :
  #   printError(e)
  #   return False
  # else :
  #   status_code = response.status_code
  #   if status_code == 200 :
  #     return True
  #   else :
  #     return False
  return True

################################################################

def manageMiner(miner, fleetParam) :
  global pollIter
  incFreq = False
  decFreq = False

  fleetName = fleetParam["name"]

  critAsicTemp = fleetParam["crit_asictemp"]
  if not isNumber(critAsicTemp) :
    raise(ValueError)

  critVRTemp = fleetParam["crit_vrtemp"]
  if not isNumber(critVRTemp) :
    raise(ValueError)

  defFreq = fleetParam["def_freq"]
  if not isNumber(defFreq) :
    raise(ValueError)

  defCoreVolt = fleetParam["def_corevolt"]
  if not isNumber(defCoreVolt) :
    raise(ValueError)

  minFreq = fleetParam["min_freq"]
  if not isNumber(minFreq) :
    raise(ValueError)

  maxFreq = fleetParam["max_freq"]
  if not isNumber(maxFreq) :
    raise(ValueError)

  minCoreVolt = fleetParam["min_corevolt"]
  if not isNumber(minCoreVolt) :
    raise(ValueError)

  maxCoreVolt = fleetParam["max_corevolt"]
  if not isNumber(maxCoreVolt) :
    raise(ValueError)

  maxAsicTemp = fleetParam["max_asictemp"]
  if not isNumber(maxAsicTemp) :
    raise(ValueError)

  maxVRTemp = fleetParam["max_vrtemp"]
  if not isNumber(maxVRTemp) :
    raise(ValueError)

  maxWatt = fleetParam["max_watt"]
  if not isNumber(maxWatt) :
    raise(ValueError)

  maxError = fleetParam["max_error"]
  if not isNumber(maxError) :
    raise(ValueError)
  else :
    if maxError > 100 :
      maxError = 100

  url = "http://" + miner + "/api/system/info"
  try :
    response = requests.get(url, timeout=2)
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
        curFreq = minerInfo['frequency']
        curCoreVolt = minerInfo['coreVoltage']
        curWatt = minerInfo['power']
        try :
          curError = minerInfo['errorPercentage']
        except KeyError as e :
          curError = maxError

        deltaVolt = 0
        deltaFreq = 0

        if pollIter % 5 == 0 :
          decFreq = True
          incFreq = False
        else :
          decFreq = False
          incFreq = True

        if curAsicTemp > maxAsicTemp or curVRTemp > maxVRTemp or curWatt > maxWatt :
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
            if curCoreVolt > minCoreVolt :
              if decFreq :
                deltaVolt = -5
              else :
                deltaVolt = -2
            if curFreq >= defFreq :
              if decFreq :
                deltaFreq = -1
            elif curFreq > minFreq :
              deltaFreq = -1
        else :
          if (curCoreVolt < maxCoreVolt) and (curError > maxError) :
            deltaVolt = 3
          if curFreq < maxFreq and incFreq :
            deltaFreq = 1

        if deltaVolt != 0 or deltaFreq != 0 :
          mnrVolt = curCoreVolt + deltaVolt
          mnrFreq = curFreq + deltaFreq

          if mnrVolt < minCoreVolt :
            mnrVolt = minCoreVolt
          elif mnrVolt > maxCoreVolt :
            mnrVolt = maxCoreVolt

          if mnrFreq < minFreq :
            mnrFreq = minFreq
          elif mnrFreq > maxFreq :
            mnrFreq = maxFreq

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
            response = requests.patch(url, json=data, headers=headers, timeout=2)
          except requests.RequestException as e :
            printError(e)
            return False
          else :
            status_code = response.status_code
            if status_code == 200 :
              return True
            else :
              return False
        else :
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

################################################################

if readConfig() :
  if runManager :
    try :
      for fleet in farm :
        fleetMiners = fleet["miners"]
        with ThreadPoolExecutor(max_workers = len(fleetMiners)) as executor:
          for miner in fleetMiners :
              executor.submit(initializeMiner, miner, fleet)
    except ValueError as e :
      printError(e)
      sys.exit(1)
    else:
      time.sleep(pollInterval)

  while runManager :
    try :
      for fleet in farm :
        fleetMiners = fleet["miners"]
        with ThreadPoolExecutor(max_workers = len(fleetMiners)) as executor :
          for miner in fleetMiners :
            executor.submit(manageMiner, miner, fleet)
    except ValueError as e :
      printError(e)
      sys.exit(1)
    else :
      if pollIter < 5 :
        pollIter += 1
      else :
        pollIter = 1
      time.sleep(pollInterval)
      readConfig()


#  set minimum operating parameters before exit
  if not runManager :
    for fleet in farm :
      fleetMiners = fleet["miners"]
      with ThreadPoolExecutor(max_workers = len(fleetMiners)) as executor:
        for miner in fleetMiners :
            executor.submit(setToMinimum, miner, fleet)
    time.sleep(5)

  print("End")
  sys.exit(0)
else :
  sys.exit(1)
