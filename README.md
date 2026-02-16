# Bitaxe Temperature Manager

Manage asic and vr temperature by automatically adjusting frequency and core voltage.

---

### Project motivation

1. I'm too lazy to check miner temperatures and update operating parameters repeatedly and manually.
2. I want to ensure my miners don’t overheat while running when I’m away from home.

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
  `false` - (default) stop currently running instance / prevent new instance from running

  `poll_interval (integer)` <br>
  time interval (seconds) between successive checks, minimum value is 5

  `farm (array of objects)` <br>
  comma separated list of fleet objects <br>
  miner operating parameters

  `name (string)` <br>
  fleet name

  `miners (array of strings)` <br>
  comma separated list of miner ip addresses

  `crit_asictemp (integer)` <br>
  `crit_vrtemp (integer)` <br>
  if asic or vr temperature rises above these values then miner frequency and core voltage will be set to user defined minimum

  `def_freq (integer)` <br>
  `def_corevolt (integer)` <br>
  miner parameters are set to these default values on script start

  `min_freq (integer)` <br>
  `max_freq (integer)` <br>
  user defined ASIC frequency range <br>
  min_freq = underclock target frequency <br>
  max_freq = overclock target frequency

  `min_corevolt (integer)` <br>
  `max_corevolt (integer)` <br>
  user defined core voltage range <br>
  min_corevolt = underclock target core voltage <br>
  max_corevolt = overclock target core voltage

  `max_asictemp (integer)` <br>
  if current ASIC temperature is above this value then frequency/core voltage is gradually reduced, else frequency/core voltage is increased within user defined limits

  `max_vrtemp (integer)` <br>
  if current voltage regulator temperature is above this value then frequency/core voltage is gradually reduced, else frequency/core voltage is increased within user defined limits

  `max_watt (integer)` <br>
  max value should not exceed 80% of your PSU wattage rating

  if current miner power usage is above this value then frequency/core voltage is gradually reduced within user defined limits

  `max_error (integer)` <br>
  if current error rate is above this value then frequency/core voltage is gradually increased within user defined limits

**_farm_** - composed of miner fleets <br>
**_fleet_** - set of miners in the farm that share the same operating parameters

---

### Usage

> Linux

`python3 Bitaxe_Temperature_Manager.py config.json`

> Windows

`python Bitaxe_Temperature_Manager.py config.json`
