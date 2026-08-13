# Bitaxe Temperature Manager

Manage asic and vr temperature by automatically adjusting frequency and core voltage.

---

### Project motivation

1. I'm too lazy to check miner temperatures and update operating parameters repeatedly and manually.
2. I want to ensure my miners don’t overheat while running when I’m away.

---

### Warning

This script modifies hardware settings, **use at your own risk**.

---

### Prerequisites

Python 3.11 or higher <br>
Bitaxe miner <br>

---

### Installation

- Download the zip archive (https://github.com/jayvm0/Bitaxe_Temperature_Manager/archive/refs/heads/main.zip)
- Create a new directory for the Python script and virtual environment (ex. jayvm0)
- Extract files from the zip archive to this directory
- Create and activate a virtual environment

  > Linux

  `cd jayvm0` <br>
  `python3 -m venv .venv` <br>
  `source .venv/bin/activate` <br>

  > Windows

  `cd jayvm0` <br>
  `python -m venv .venv` <br>
  `.venv\Scripts\activate.bat` <br>

- Install dependencies

  `pip install -r requirements.txt`

---

### Configuration

- edit **config.json**

  `name` _(string)_ <br>
  farm name

  `run_manager (boolean)` <br>
  `true` - allow new instance to run <br>
  `false` - (default) stop the currently running instance or prevent new instances from starting

  `poll_interval (integer)` <br>
  time interval (seconds) between successive checks, minimum value is 5

  `farm (array of objects)` <br>
  comma separated list of fleet (set of miners in the farm that share the same operating parameters) objects <br>
  miner operating parameters

  `name (string)` <br>
  fleet name

  `miners (array of strings)` <br>
  comma separated list of miner ip addresses

  `crit_asictemp (integer)` <br>
  `crit_vrtemp (integer)` <br>
  if the ASIC or VR temperature rises above these values, the miner frequency and core voltage will be set to the user-defined minimum

  `def_freq (integer)` <br>
  `def_corevolt (integer)` <br>
  miner parameters are set to these default values at the start of the script

  `min_freq (integer)` <br>
  `max_freq (integer)` <br>
  user defined ASIC frequency range, ASIC frequency will not exceed this range <br>

  `min_corevolt (integer)` <br>
  `max_corevolt (integer)` <br>
  user defined core voltage range, core voltage will not exceed this range

  `max_asictemp (integer)` <br>
  if the current ASIC temperature exceeds this value, the frequency and core voltage are gradually reduced; otherwise, they are increased within the user-defined range

  `max_vrtemp (integer)` <br>
  if the current voltage regulator temperature is above this value, the frequency/core voltage is gradually reduced; otherwise, the frequency/core voltage is increased within the user-defined range

  `max_watt (integer)` <br>
  maximum value should not exceed 80% of your PSU wattage rating <br>
  if the current miner power usage is above this value, the frequency/core voltage is gradually reduced within the user-defined range

  `max_error (integer)` <br>
  if the current error rate is above this value, the frequency/core voltage is gradually increased within the user-defined range

---

### Usage

> Linux

`python3 Bitaxe_Temperature_Manager.py config.json`

> Windows

`python Bitaxe_Temperature_Manager.py config.json`
