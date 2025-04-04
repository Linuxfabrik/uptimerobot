# YAML Syntax for UptimeRobot CLI

This YAML format is used by the UptimeRobot CLI tool (implemented in [utr.py](https://github.com/Linuxfabrik/uptimerobot/blob/main/src/utr.py) and [uptimerobot.py](https://github.com/Linuxfabrik/lib/blob/main/uptimerobot.py)) to manage monitors, maintenance windows (mwindows), and alert contacts in a stateful way via the UptimeRobot API. The format is heavily inspired by the [Uptime Robot API documentation](https://uptimerobot.com/api).

The CLI tool processes the YAML file to compare the desired state (as defined in the file) with what exists in your UptimeRobot account. It then creates, updates, or deletes resources accordingly. By default, if certain fields are omitted, the tool will generate defaults (for example, auto-generating a friendly name for monitors if none is provided, or defaulting the monitor type to `"http"`).

---

## Top-Level Structure

The YAML file can define one or more of the following top-level keys:

- **monitors**: A list of monitor definitions.
- **mwindows**: A list of maintenance window definitions.
- **alert_contacts**: A list of alert contact definitions (note: due to API limitations, creation and update are not supported for alert contacts).
- **psps**: A list of status pages (note: due to API limitations, you can't provide all the settings the GUI offers).

---

## `monitors`

* **Type**: sequence of mappings

Each monitor entry defines a check for a website or API endpoint. For a complete list of fields, have a look at the [Uptime Robot API documentation](https://uptimerobot.com/api) > newMonitor or editMonitor.

### Fields

- **`alert_contacts`**  
  *Type*: sequence of mappings  
  A list of alert contact configurations for this monitor. Each entry should include:
  
  - **`friendly_name`**: A name to identify the alert contact.
  - **`threshold`**: The number of consecutive failures required before triggering an alert.
  - **`recurrence`**: The interval (in minutes) for recurring alerts (set to `0` to disable recurrence).

- **`auth_type`**  
  *Type*: string  
  Allowed values include:
  - `"basic"`
  - `"digest"`

- **`disable_domain_expire_notifications`**  
  *Type*: string  
  Allowed values include:
  - `"enable"`
  - `"disable"`

- **`friendly_name`**  
  *Type*: string  
  A descriptive name for the monitor. If omitted, the tool auto-generates one by combining the `prefix` and `url` (with URL scheme removed).

- **`http_auth_type`**  
  *Type*: string  
  Allowed values include:
  - `"basic"`
  - `"digest"`

- **`http_method`**  
  *Type*: string  
  Allowed values include:
  - `"head"`
  - `"get"`
  - `"post"`
  - `"put"`
  - `"patch"`
  - `"delete"`
  - `"options"`

- **`interval`**  
  *Type*: number  
  The interval (in seconds) between consecutive checks.

- **`keyword_case_type`**  
  *Type*: string  
  Allowed values include:
  - `"cs"`: case-sensitive
  - `"ci"`: case-insensitive

- **`keyword_type`**  
  *Type*: string  
  Allowed values include:
  - `"exist"`: start incidence when keyword exists
  - `"notex"`: start incidence when keyword does not exist

- **`mwindows`**  
  *Type*: sequence (or a single value)  
  A reference to one or more maintenance windows. These can be provided by specifying either their friendly name (if pre-existing) or their ID. When processing the YAML, the CLI tool matches these values with existing mwindows and associates them with the monitor.

- **`post_content_type`**  
  *Type*: string  
  Allowed values include:
  - `"text/html"`
  - `"content/json"`

- **`post_type`**  
  *Type*: string  
  Allowed values include:
  - `"key"`
  - `"raw"`

- **`prefix`** (specific to this tool)  
  *Type*: string  
  A short identifier used as part of the monitor’s identification. It is also used to help generate a default friendly name if none is provided.

- **`state`** (specific to this tool)  
  *Type*: string  
  Indicates the desired state of the monitor:
  - `"present"` (default): The monitor should exist (create it if not found, update if it exists).
  - `"absent"`: The monitor should be deleted if it exists.

- **`status`**  
  *Type*: string  
  Allowed values include:
  - `"active"`
  - `"paused"`

- **`sub_type`**  
  *Type*: string  
  Allowed values include:
  - `"http"`
  - `"https"`
  - `"ftp"`
  - `"smtp"`
  - `"pop3"`
  - `"imap"`
  - `"custom"`

- **`type`**  
  *Type*: string  
  The type of the monitor. Defaults to `"http"` if not provided. Other possible values (handled internally via a conversion mapping) include `"ping"`, `"keyw"`, `"port"`, and `"beat"`.

- **`url`** (required)  
  *Type*: string  
  The URL of the endpoint to monitor. This is the target for uptime checks. Has to be unique in your UptimeRobot account.

---

## `mwindows`

* **Type**: sequence of mappings

Each maintenance window (mwindow) entry defines a time period during which uptime checks might be suppressed or treated differently. For a complete list of fields, have a look at the [Uptime Robot API documentation](https://uptimerobot.com/api) > newMWindow or editMWindow.


### Fields

- **`duration`**  
  *Type*: number  
  The length of the maintenance window in minutes. If not provided, it is computed from `start_time` and `end_time`.

- **`end_time`** (specific to this tool)  
  *Type*: string  
  The end time of the window. Acceptable formats are `"HH:MM"` or `"HH:MM:SS"`.  
  _Note_: If the `duration` is omitted, it is automatically calculated as the difference between `end_time` and `start_time` (in minutes).

- **`friendly_name`**  
  *Type*: string  
  A descriptive name for the maintenance window. If omitted, a default is generated. For windows of type `"weekly"` or `"monthly"`, the friendly name typically includes the window type, the day(s) (from the `value` field), and the time range. For other types (e.g. `"daily"`), it includes the time range only.

- **`start_time`**  
  *Type*: string  
  The start time of the window. Acceptable formats are `"HH:MM"` or `"HH:MM:SS"`.

- **`state`** (specific to this tool)  
  *Type*: string  
  Indicates whether the maintenance window should exist:
  - `"present"` (default): Create or update the mwindow.
  - `"absent"`: Delete the mwindow if it exists.

- **`status`**  
  *Type*: string  
  Allowed values include:
  - `"active"`
  - `"paused"`

- **`type`**  
  *Type*: string  
  Specifies the recurrence type of the window. Allowed values include:
  - `"once"`
  - `"daily"`
  - `"weekly"`
  - `"monthly"`

- **`value`**  
  *Type*: string  
  For recurring windows (especially `"weekly"` or `"monthly"`), this field indicates the day of the week (e.g., `"mon"`, `"tue"`, etc.) or other value needed by the API.

---

## `alert_contacts`

* **Type**: sequence of mappings

Each alert contact entry defines a recipient or method for receiving alerts when a monitor detects downtime or other issues.

### Fields

- **`id`**  
  *Type*: number  
  The ID of the alert contact to be managed.

- **`state`** (specific to this tool)  
  *Type*: string  
  Indicates whether the maintenance window should exist:
  - `"present"` (default): Create or update the alert contact.
  - `"absent"`: Delete the alert contact if it exists.  
  Although supported in the YAML format, note that due to API limitations for alert contacts, `utr` refuses to create or update alert contacts. Only deletion is supported when `state` is set to `"absent"`.

---

## `psps`

* **Type**: sequence of mappings

Each entry defines a status page (PSP). For a complete list of fields, have a look at the [Uptime Robot API documentation](https://uptimerobot.com/api) > newPSP or editPSP.

### Fields

- **`monitors`**  
  *Type*: sequence of mappings  
  List of monitors, identified by `friendly_name` or `id`.

- **`sort`**  
  *Type*: string  
  Allowed values include:
  - `"a-z"`
  - `"z-a"`
  - `"up-down-paused"`
  - `"down-up-paused"`

- **`status`**  
  *Type*: string  
  Allowed values include:
  - `"active"`
  - `"paused"`

- **`state`** (specific to this tool)  
  *Type*: string  
  Indicates whether the status page should exist:
  - `"present"` (default): Create or update the PSP.
  - `"absent"`: Delete the PSP if it exists.

---

## Usage

The UptimeRobot CLI tool supports the `apply` command which uses a YAML file to manage your UptimeRobot resources. It reads the YAML file and synchronises your UptimeRobot account by creating, updating or deleting monitors, mwindows and alert contacts as needed. Here is an example of a minimal YAML file that demonstrates some features:

```
alertcontacts:
  - id: 47110815
    state: 'absent'

mwindows:
  - type: 'weekly'
    value: 'fri'
    start_time: '03:30'
    end_time: '05:30'
    status: 'active'

monitors:
  - url: 'https://www.linuxfabrik.ch'
    http_method: 'get'
    interval: 300
    mwindows:
      - friendly_name: 'weekly fri 03:30-05:30'

  - friendly_name: 'www.google.ch'
    state: 'absent'

psps:
  - friendly_name: 'Status - Linuxfabrik'
    custom_url: ''
    monitors:
      - friendly_name: '001 www.linuxfabrik.ch'
      - id: 798324818
      - id: 793467491
    sort: 'a-z'
    status: 'active'
    state: 'present'
```

Applying the YAML file to your UptimeRobot account:

    ./utr apply uptimerobot.yml

