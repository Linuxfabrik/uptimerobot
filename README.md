# utr - UptimeRobot CLI

`utr` is a CLI tool for UptimeRobot to help manage monitors, MWindows, etc. in a stateful way either by using a YAML file or by command line actions.


## Features

- **Retrieve Account Information:**  
  Display account details including monitor counts, SMS credits, and rate limits.

- **Manage Monitors:**  
  List, create, update, and delete monitors. Automatically convert human-friendly monitor definitions into the required UptimeRobot API format.

- **Manage Maintenance Windows (MWindows):**  
  List, create, update, or delete maintenance windows based on your YAML definitions.

- **Manage Alert Contacts:**  
  Retrieve and update alert contacts. (Note: Creating/updating alert contacts is limited by the API.)

- **Command-line and YAML Support:**  
  Use the tool directly from the command line for quick actions or maintain a YAML file to keep your configuration stateful and version-controlled.

- **Flexible Output Formats:**  
  Output data in either `yaml` or a human-friendly table format, with an option for extended reporting.


## Prerequisites

- **Python 3:**  
  Ensure you have Python 3 installed on your system.

- **UptimeRobot API Key:**  
  You need a valid UptimeRobot API key. You can provide it directly via the command line using `--api_key` or store it in a file (default: `~/.uptimerobot`) and reference it with `--api_key_file` (default: `~/.uptimerobot`.

- **Required Python Libraries:**  
  The tool depends on some libraries, like the Linuxfabrik Python Libraries, or `pyyaml`.


## Installation

1. **Clone or Download the Repository:**  
   `git clone https://github.com/Linuxfabrik/uptimerobot.git`

2. **Install Dependencies:**  
  `cd uptimerobot && python3 -m pip install --user --requirement requirements.txt --require-hashes`

3. **Set Up Your API Key:**  
  Either create a file (by default at `~/.uptimerobot`) containing your [API key](https://dashboard.uptimerobot.com/integrations) or pass it using the `--api_key` flag when running the tool.

4. **Make the Script Executable:**  
  If necessary, make the script executable: `chmod +x utr`


## Usage

The tool supports several commands using subcommands. The commands support all [UptimeRobot API parameters](https://uptimerobot.com/api/). Below are the primary commands and their functions:


### Getting help

Examples:

    ./utr --help
    ./utr get --help
    ./utr get monitors --help


### Global Options

- `--api_key`  
  Provide your UptimeRobot API key directly. This option overrides the API key file.

- `--api_key_file`  
  Specify the path to the file containing your UptimeRobot API key. *(Default: `~/.uptimerobot`)*


### Commands

#### 1. `get`

Retrieve information from UptimeRobot. Available resources:

- **account**  
  Run `./utr get account` to display account details, including monitor usage, SMS credits, and rate limits.

- **monitors**  
  Run `./utr get monitors [--output=yaml|table] [--lengthy]` to list monitors with details like friendly name, URL, type, and more. Use `--output` to choose the format (default is `table`) and `--lengthy` for extended information (only for table output).

- **alert_contacts**  
  Run `./utr get alert_contacts [--output=yaml|table] [--lengthy]` to retrieve and display alert contact information.

- **mwindows**  
  Run `./utr get mwindows [--output=yaml|table] [--lengthy]` to list maintenance windows with start time, end time, duration, and status.

- **psps**  
  Run `./utr get psps [--output=yaml|table] [--lengthy]` *(Note: This resource is currently not implemented.)*


#### 2. `apply`

Apply changes defined in a YAML file to your UptimeRobot account. This command processes your YAML definitions for monitors, maintenance windows, and alert contacts, and performs create, update, or delete actions accordingly.

Run `./utr apply /path/to/config.yaml` where the YAML file should contain definitions for:
- `monitors`
- `mwindows`
- `alert_contacts`
- `psps` *(currently not implemented)*

*The tool will automatically convert user-friendly values to the appropriate UptimeRobot API format.*


#### 3. `set`

Update data for a specific resource from the command line. Currently, this command supports updating monitors.

Run `./utr set monitors [--field=value ...]`  
Additional filtering options can be passed as `--field=value` parameters to target specific monitors.

*Other resources (`account`, `alert_contacts`, `mwindows`, `psps`) are marked as "todo" and are not yet implemented.*


## The YAML file

A minimal YAML file example:

```
alertcontacts:
  - id: 47110815
    state: 'absent'

mwindows:
  - type: 'weekly'
    value: 'mon'
    start_time: '03:30'
    end_time: '05:30'
    status: 'active'

monitors:
  - url: 'https://www.linuxfabrik.ch'
    http_method: 'get'
    interval: 300
    mwindows:
      - friendly_name: 'weekly mon 03:30-05:30'
```

Applying the YAML file to your UptimeRobot account:

    ./utr apply uptimerobot.yml


### "monitors"

Used to create, update or delete monitors. See [api/#newMonitorWrap](https://uptimerobot.com/api/#newMonitorWrap) for a list of attributes. Feel free to use user-friendly values instead of the numeric ones documented in the UptimeRobot API.

Required attributes:

* url: Value has to be unique. If there are duplicates, updates to the last monitor found will be applied.

If "friendly_name" is ommitted, one is automatically created in the format "prefix url" (or just "url" if "prefix" is not provided). "http://" and "https://" is always stripped from "friendly_name".

If "type" is ommitted, "type: http" is used.

Attributes specific to this tool:

* prefix: a string
* state: 'present' (default) or 'absent'

This example results in two monitors to be created or updated:

```
monitors:
  # minimal example; results in a monitor named "example.com"
  - url: 'https://example.com'

  # results in a monitor named "internal www.example.com"
  - prefix: 'internal'  # tool-specific
    state: 'present'
    url: 'https://www.example.com'
    interval: 30

  # a more complex example
  - friendly_name: 'https://mon.example.com/icingaweb2/'
    http_method: 'get'
    http_auth_type: 'basic'
    http_username: 'linuxfabrik'
    http_password: 'linuxfabrik'
    mwindows:
      - friendly_name: 'weekly wed 03:30-05:30'
    alert_contacts:
      - friendly_name: 'web-hook down event to rocket.chat'
        threshold: 1
        recurrence: 0
      - friendly_name: 'web-hook up event to rocket.chat'
        threshold: 1
        recurrence: 0
      - friendly_name: 'web-hook ssl & domain expiry to rocket.chat'
        threshold: 1
        recurrence: 0
      - id: 4711
    state: 'present'
```

http_auth_type:

    1: 'basic'
    2: 'digest'

http_method:

    1: 'head'
    2: 'get'
    3: 'post'
    4: 'put'
    5: 'patch'
    6: 'delete'
    7: 'options'

keywcase:

    0: 'cs' (= case-sensitive)
    1: 'ci' (= case-insentive)

keywtype:

    1: 'exist'
    2: 'notex'

status, statuses:

    0: 'paused'
    1: 'wait'
    2: 'up'
    8: 'down?'
    9: 'down'

type, types:

    1: 'http'
    2: 'keyw'
    3: 'ping'
    4: 'port'
    5: 'beat'


### "mwindows"

You may use "end_time" instead of "duration".

If "friendly_name" is ommitted, one is automatically created in the format "type value1,value2 start_time-end_time"

```
mwindows:
  - type: 'daily'
    start_time: '21:22'
    end_time: '21:32'
    status: 'active'
    state: 'present'

  - type: 'weekly'
    value: 'mon'
    start_time: '03:30'
    end_time: '05:30'
    status: 'active'
    state: 'present'
```

type:

    1: 'once'
    2: 'daily'
    3: 'weekly'
    4: 'monthly'

value:

    1: 'mon'
    2: 'tue'
    3: 'wed'
    4: 'thu'
    5: 'fri'
    6: 'sat'
    7: 'sun'


### "alert_contacts"

The API is limited here, so we currently just support deletion of alert contacts.

```
alert_contacts:

- id: 3654399
  state: 'absent'

- friendly_name: 'example-group'
  state: 'absent'
```


## Usage examples

- **Retrieve Account Details:**  
  `./utr get account --api_key YOUR_API_KEY`

- **List Monitors containing "example" (within `url` or `friendly_name`), in a brief table format:**  
  `./utr get monitors --output=table --search=example --api_key YOUR_API_KEY`

- **List some specific Monitors in YAML Format:**  
  `./utr get monitors  --types=keyw --http_request_details=true --output=yaml`

- **Get all monitors with type 2, 4 and 5:**  
  `./utr get monitors --types=2-4-5`

- **The same using user-friendly parameter values:**  
  `./utr get monitors --types=keyw-port-beat --statuses=paused-down`

- **Apply Changes from a YAML File:**
  `./utr apply /home/admin/uptime_config.yaml`

- **Update Monitors Using Command-Line Options - Pausing and resuming some monitors at once:**  
  `./utr set monitors --search=example --status=pause`
  `./utr set monitors --search=example --status=start`


## Troubleshooting & Notes

- **API Limitations:**
  Some operations (e.g., creating or updating alert contacts) are limited by the UptimeRobot API. The tool prints informative messages when certain actions cannot be performed.

- **Field Filters:**
  Additional `--field=value` options can be passed to refine API requests. These filters are processed automatically and applied to the corresponding API calls.

- **Error Handling:**
  In case of errors (such as a missing API key), the tool provides descriptive messages and exits gracefully.


## Credits, License

* Authors: [Linuxfabrik GmbH, Zurich](https://www.linuxfabrik.ch)
* License: The Unlicense, see [LICENSE file](https://unlicense.org/)
