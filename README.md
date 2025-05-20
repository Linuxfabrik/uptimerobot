# utr - UptimeRobot CLI

`utr` is a CLI tool for UptimeRobot to help manage monitors, maintenance windows, alert contacts and status pages in a stateful way either by using a YAML file or by command line actions.


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

```
pip install uptimerobot-cli
utr --help
```


## Usage

The tool supports several commands using subcommands. The commands support all [UptimeRobot API parameters](https://uptimerobot.com/api/). Below are the primary commands and their functions:


### Getting help

Examples:

    utr --help
    utr get --help
    utr get monitors --help


### Global Options

- `--api_key`  
  Provide your UptimeRobot API key directly. This option overrides the API key file.

- `--api_key_file`  
  Specify the path to the file containing your UptimeRobot API key. *(Default: `~/.uptimerobot`)*


### Commands

#### 1. `get`

Retrieve information from UptimeRobot. Available resources:

- **account**  
  Run `utr get account` to display account details, including monitor usage, SMS credits, and rate limits.

- **monitors**  
  Run `utr get monitors [--output=yaml|table] [--lengthy]` to list monitors with details like friendly name, URL, type, and more. Use `--output` to choose the format (default is `table`) and `--lengthy` for extended information (only for table output).

- **alert_contacts**  
  Run `utr get alert_contacts [--output=yaml|table] [--lengthy]` to retrieve and display alert contact information.

- **mwindows**  
  Run `utr get mwindows [--output=yaml|table] [--lengthy]` to list maintenance windows with start time, end time, duration, and status.

- **psps**  
  Run `utr get psps [--output=yaml|table] [--lengthy]` *(Note: This resource is currently not implemented.)*


#### 2. `apply`

Apply changes defined in a YAML file to your UptimeRobot account. This command processes your YAML definitions for monitors, maintenance windows, and alert contacts, and performs create, update, or delete actions accordingly.

Run `utr apply /path/to/config.yaml` where the YAML file should contain definitions for:
- `monitors`
- `mwindows`
- `alert_contacts`
- `psps` *(currently not implemented)*

*The tool will automatically convert user-friendly values to the appropriate UptimeRobot API format.*


#### 3. `set`

Update data for a specific resource from the command line. Currently, this command supports updating monitors.

Run `utr set monitors [--field=value ...]`  
Additional filtering options can be passed as `--field=value` parameters to target specific monitors.

*Other resources (`account`, `alert_contacts`, `mwindows`, `psps`) are marked as "todo" and are not yet implemented.*


## YAML file for applying updates to the UptimeRobot configuration

For the documentation of the YAML format used by the UptimeRobot CLI, please refer to the [YAML syntax documentation](yaml.md).


## Usage examples

- **Retrieve Account Details:**  
  `utr get account --api_key YOUR_API_KEY`

- **List Monitors containing "example" (within `url` or `friendly_name`), in a brief table format:**  
  `utr get monitors --output=table --search=example --api_key YOUR_API_KEY`

- **List some specific Monitors in YAML Format:**  
  `utr get monitors  --types=keyw --http_request_details=true --output=yaml`

- **Get all monitors with type 2, 4 and 5:**  
  `utr get monitors --types=2-4-5`

- **The same using user-friendly parameter values:**  
  `utr get monitors --types=keyw-port-beat --statuses=paused-down`

- **Apply Changes from a YAML File:**  
  `utr apply /home/admin/uptime_config.yaml`

- **Bulk update monitors using command-line options - pausing and resuming some monitors at once:**  
  `utr set monitors --search=example --status=paused`
  `utr set monitors --search=example --status=up`

- **Bulk update all status pages**
  `utr set psps --status=paused`
  `utr set psps --status=active`


## Troubleshooting & Notes

- **API Limitations:**  
  Some operations (e.g., creating or updating alert contacts) are limited by the UptimeRobot API. The tool prints informative messages when certain actions cannot be performed.

- **Keys and Values:**  
  Additional `--key=value` options can be passed to refine API requests. These filters are processed automatically and applied to the corresponding API calls.


## Credits, License

* Authors: [Linuxfabrik GmbH, Zurich](https://www.linuxfabrik.ch)
* License: The Unlicense, see [LICENSE file](https://unlicense.org/)
