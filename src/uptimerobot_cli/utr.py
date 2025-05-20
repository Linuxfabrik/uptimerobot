# -*- coding: utf-8; py-indent-offset: 4 -*-
#
# Author:  Linuxfabrik GmbH, Zurich, Switzerland
# Contact: info (at) linuxfabrik (dot) ch
#          https://www.linuxfabrik.ch/
# License: The Unlicense, see LICENSE file.

"""See the README for more details.
"""

import argparse  # pylint: disable=C0413
import os  # pylint: disable=C0413
import sys  # pylint: disable=C0413
from datetime import datetime, timedelta

import yaml  # pylint: disable=C0413

import lib.base  # pylint: disable=C0413
import lib.disk  # pylint: disable=C0413
import lib.txt  # pylint: disable=C0413
import lib.uptimerobot  # pylint: disable=C0413



__author__ = 'Linuxfabrik GmbH, Zurich/Switzerland'
__version__ = '2025032701'

DESCRIPTION = """A CLI tool for UptimeRobot to help manage monitors, MWindows, etc. in a
                 stateful way using a YAML file or by command line actions."""

DEFAULT_API_KEY_FILE = '~/.uptimerobot'
DEFAULT_LENGTHY = False


def parse_args():
    """Parse command line arguments using argparse.
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'%(prog)s: v{__version__} by {__author__}'
    )

    # Global options
    parser.add_argument(
        '--api_key',
        help='Provide your UptimeRobot API key directly. This option overrides the API key file.',
        dest='API_KEY',
    )

    parser.add_argument(
        '--api_key_file',
        help='Specify the path to the file containing your UptimeRobot API key. '
             'Default: %(default)s',
        dest='API_KEY_FILE',
        default=DEFAULT_API_KEY_FILE,
    )


    # One level of subparsers for the main command.
    subparsers = parser.add_subparsers(
        dest='COMMAND',
        help='Available commands',
    )


    # "apply" command that uses a positional argument for the resource.
    apply_parser = subparsers.add_parser(
        'apply',
        help='Apply information from yaml file to your UptimeRobot account,',
    )
    apply_parser.add_argument(
        dest='YMLFILE',
        help='Path to yaml file. ',
    )


    # "get" command that uses a positional argument for the resource.
    get_parser = subparsers.add_parser(
        'get',
        help='Retrieve information from UptimeRobot.',
    )
    get_parser.add_argument(
        dest='RESOURCE',
        help='Resource to retrieve',
        choices=['account', 'monitors', 'alert_contacts', 'mwindows', 'psps'],
    )
    # --output option applies to all resources except "account".
    get_parser.add_argument(
        '--output',
        help='Output format (ignored for "account"). '
             'Default: %(default)s',
        dest='OUTPUT',
        choices=['yaml', 'table'],
        default='table',
    )
    get_parser.add_argument(
        '--lengthy',
        help='Extended reporting (only for `--output=table`). '
             'Default: %(default)s',
        dest='LENGTHY',
        action='store_true',
        default=DEFAULT_LENGTHY,
    )


    # "set" command that uses a positional argument for the resource.
    set_parser = subparsers.add_parser(
        'set',
        help='Update data from the command-line.',
    )
    set_parser.add_argument(
        dest='RESOURCE',
        help='Resource to update',
        choices=['account', 'monitors', 'alert_contacts', 'mwindows', 'psps'],
    )


    # Parse the above known arguments; any additional "--field=value" options are kept as unknown
    # (which are used to filter api requests).
    args, unknown = parser.parse_known_args()

    # Process additional options of the form --field=value into a dictionary.
    field_filters = {}
    for arg in unknown:
        if arg.startswith('--'):
            stripped = arg.lstrip('-')
            if '=' in stripped:
                key, value = stripped.split('=', 1)
                field_filters[key] = value
            else:
                field_filters[stripped] = True
    args.field_filters = field_filters

    return args


def unknown_command(args):
    lib.base.cu(f'Unknown or missing command `{args.COMMAND}`')


def get_account_details(args):
    _, account, rl = lib.uptimerobot.get_account_details({
        'api_key': args.API_KEY,
    })
    a = account[0]
    msg = 'Account:\n'
    msg += f'* {a["down_monitors"]}/{a["paused_monitors"]}/{a["up_monitors"]} (down/paused/up), '
    msg += f'{a["total_monitors_count"]}/{a["monitor_limit"]} '
    msg += f'{lib.txt.pluralize("monitor", a["monitor_limit"])} used '
    msg += f'({int(a["total_monitors_count"]/a["monitor_limit"] * 100)}%)\n'
    msg += f'* {a["sms_credits"]} SMS credits\n'
    msg += f'* Payment Period: {a["payment_period"]}, '
    msg += f'Subscription expires: {a["subscription_expiry_date"]}\n'
    msg += f'* Account: {a["firstname"]} ({a["email"]})\n\n'

    msg += 'Rate Limits:\n'
    msg += f'* {rl["x-ratelimit-remaining"]}/{rl["x-ratelimit-limit"]} calls left in current duration\n'
    msg += f'* Rate limiting period will end at {lib.time.epoch2iso(rl["x-ratelimit-reset"])}'

    lib.base.oao(msg)


def get_monitors(args):
    params = args.field_filters
    params.update({'api_key': args.API_KEY})
    # useful especially in yaml result list
    if 'alert_contacts' not in params:
        params.update({'alert_contacts': 1})
    if 'auth_type' not in params:
        params.update({'auth_type': True})
    if 'custom_http_headers' not in params:
        params.update({'custom_http_headers': True})
    if 'custom_http_statuses' not in params:
        params.update({'custom_http_statuses': True})
    if 'http_request_details' not in params:
        params.update({'http_request_details': True})
    if 'mwindows' not in params:
        params.update({'mwindows': 1})
    if 'ssl' not in params:
        params.update({'ssl': 1})

    monitors = lib.base.coe(lib.uptimerobot.get_monitors(params))
    for i, item in enumerate(monitors):
        if args.OUTPUT == 'table':
            if item['http_username']:
                monitors[i]['creds'] = '*****'
            else:
                monitors[i]['creds'] = ''
            monitors[i]['mwindows'] = len(item['mwindows'])
            monitors[i]['alert_contacts'] = len(item['alert_contacts'])
        if args.OUTPUT == 'table' and not args.LENGTHY:
            # shorten long URLs
            if len(monitors[i]['url']) > 47:
                monitors[i]['url'] = item['url'][:47] + '...'

    print(f'{len(monitors)} {lib.txt.pluralize("monitor", len(monitors))} found.')
    if args.OUTPUT == 'table':
        if args.LENGTHY:
            lib.base.oao(lib.base.get_table(
                sorted(monitors, key=lambda item: item['friendly_name']),
                [
                    'id',
                    'friendly_name',
                    'url',
                    'type',
                    'sub_type',
                    'http_method',
                    'http_username',
                    'http_password',
                    'keyword_type',
                    'keyword_case_type',
                    'keyword_value',
                    'port',
                    'interval',
                    'mwindows',
                    'alert_contacts',
                    'timeout',
                    'status',
                ],
                header=[
                    'id',
                    'friendly_name (sorted)',
                    'url',
                    'type',
                    'sub_type',
                    'http_method',
                    'http_username',
                    'http_password',
                    'kwtyp',
                    'case',
                    'kywrd',
                    'port',
                    'intrv',
                    '#mwndws',
                    '#cntcts',
                    'tmout',
                    'status',
                ],
            ))
        else:
            lib.base.oao(lib.base.get_table(
                sorted(monitors, key=lambda item: item['friendly_name']),
                [
                    'id',
                    'friendly_name',
                    'url',
                    'type',
                    'http_method',
                    'creds',
                    'keyword_type',
                    'keyword_value',
                    'interval',
                    'mwindows',
                    'alert_contacts',
                    'status',
                ],
                header=[
                    'id',
                    'friendly_name (sorted)',
                    'url',
                    'type',
                    'mthd',
                    'creds',
                    'kwtyp',
                    'kywrd',
                    'intrv',
                    '#mwndws',
                    '#cntcts',
                    'status',
                ],
            ))
    else:
        lib.base.oao(yaml.dump(monitors))


def get_mwindows(args):
    params = args.field_filters
    params.update({'api_key': args.API_KEY})

    mwindows = lib.base.coe(lib.uptimerobot.get_mwindows(params))
    for i, item in enumerate(mwindows):
        try:
            mwindows[i]['end_time'] = datetime.strptime(item['start_time'], "%H:%M:%S") + \
                timedelta(minutes=item['duration'])
            mwindows[i]['end_time'] = mwindows[i]['end_time'].strftime("%H:%M:%S")
        except:
            mwindows[i]['end_time'] = datetime.strptime(item['start_time'], "%H:%M") + \
                timedelta(minutes=item['duration'])
            mwindows[i]['end_time'] = mwindows[i]['end_time'].strftime("%H:%M")

    print(f'{len(mwindows)} {lib.txt.pluralize("mwindow", len(mwindows))} found.')
    if args.OUTPUT == 'table':
        lib.base.oao(lib.base.get_table(
            sorted(mwindows, key=lambda item: item['friendly_name']),
            [
                'id',
                'friendly_name',
                'type',
                'start_time',
                'end_time',
                'duration',
                'value',
                'status',
            ],
            header=[
                'id',
                'friendly_name (sorted)',
                'type',
                'start_time',
                'end_time',
                'duration',
                'value',
                'status',
            ],

        ))
    else:
        lib.base.oao(yaml.dump(mwindows))


def get_alert_contacts(args):
    params = args.field_filters
    params.update({'api_key': args.API_KEY})
    alert_contacts = lib.base.coe(lib.uptimerobot.get_alert_contacts(params))
    for i, item in enumerate(alert_contacts):
        if 'value' not in item:
            alert_contacts[i]['value'] = ''

    print(f'{len(alert_contacts)} {lib.txt.pluralize("alertcontact", len(alert_contacts))} found.')
    if args.OUTPUT == 'table':
        lib.base.oao(lib.base.get_table(
            sorted(alert_contacts, key=lambda item: item['friendly_name']),
            [
                'id',
                'friendly_name',
                'type',
                'value',
                'status',
            ],
            header=[
                'id',
                'friendly_name (sorted)',
                'type',
                'value',
                'status',
            ],

        ))
    else:
        lib.base.oao(yaml.dump(alert_contacts))


def get_psps(args):
    params = args.field_filters
    params.update({'api_key': args.API_KEY})

    psps = lib.base.coe(lib.uptimerobot.get_psps(params))
    print(f'{len(psps)} {lib.txt.pluralize("mwindow", len(psps))} found.')
    if args.OUTPUT == 'table':
        for i, item in enumerate(psps):
            psps[i]['monitors'] = len(item['monitors'])
        lib.base.oao(lib.base.get_table(
            sorted(psps, key=lambda item: item['friendly_name']),
            [
                'id',
                'friendly_name',
                'standard_url',
                'custom_url',
                'monitors',
                'sort',
                'status',
            ],
            header=[
                'id',
                'friendly_name',
                'standard_url',
                'custom_url',
                '#mntrs',
                'sort',
                'status',
            ],

        ))
    else:
        lib.base.oao(yaml.dump(psps))


def parse_and_preprocess_yaml(args):
    # load definitions from file
    ymlfile = lib.base.coe(lib.disk.read_file(args.YMLFILE))
    ymlfile = yaml.safe_load(ymlfile)

    if 'monitors' in ymlfile:
        for i, item in enumerate(ymlfile['monitors']):
            friendly_name = item.get('friendly_name')
            if not friendly_name:
                # make a nice consistent friendly_name "prefix url" or "url"
                friendly_name = f'{item.get("prefix", "")} {item.get("url")}'
                friendly_name = friendly_name.replace('https://', '')
                friendly_name = friendly_name.replace('http://', '')
                friendly_name = friendly_name.replace(
                    f'{item.get("prefix")} {item.get("prefix")}',
                    item.get('prefix', ''),
                )
            ymlfile['monitors'][i]['friendly_name'] = friendly_name.strip()

            # defaults:
            if not item.get('type'):
                ymlfile['monitors'][i]['type'] = 'http'

    if 'mwindows' in ymlfile:
        for i, item in enumerate(ymlfile['mwindows']):
            friendly_name = item.get('friendly_name')
            if not friendly_name:
                if item.get('type') == 'weekly' or item.get('type') == 'monthly':
                    # make a nice consistent friendly_name like "weekly mon-tue-thu 21:30-21:35"
                    friendly_name = f'{item.get("type")} {item.get("value")} {item.get("start_time", "")}-{item.get("end_time", "")}'
                else:
                    # make a nice consistent friendly_name like "daily 21:30-21:35"
                    friendly_name = f'{item.get("type")} {item.get("start_time", "")}-{item.get("end_time", "")}'
            ymlfile['mwindows'][i]['friendly_name'] = friendly_name.strip()

            # defaults:
            if item.get('state') == 'absent':
                # no more data needed
                continue
            if not item.get('duration'):
                try:
                    ymlfile['mwindows'][i]['duration'] = int(
                        lib.time.timestrdiff(
                            item['end_time'],
                            item['start_time'],
                            pattern1='%H:%M:%S',
                            pattern2='%H:%M:%S',
                        ) / 60
                    )
                except:
                    ymlfile['mwindows'][i]['duration'] = int(
                        lib.time.timestrdiff(
                            item['end_time'],
                            item['start_time'],
                            pattern1='%H:%M',
                            pattern2='%H:%M',
                        ) / 60
                    )

    return ymlfile


def apply_monitors(args, targets):
    if not 'monitors' in targets:
        return

    # get all data from uptimerobot
    actual_monitors = lib.base.coe(lib.uptimerobot.get_monitors({
        'api_key': args.API_KEY,
    }))
    actual_mwindows = lib.base.coe(lib.uptimerobot.get_mwindows({
        'api_key': args.API_KEY,
    }))
    actual_alert_contacts = lib.base.coe(lib.uptimerobot.get_alert_contacts({
        'api_key': args.API_KEY,
    }))

    print(f'Working on {len(targets["monitors"])} {lib.txt.pluralize("monitor", len(targets["monitors"]))}.')
    for target_monitor in targets['monitors']:
        # search for existing monitors (unique by URL)
        # if given, use the id directly, otherwise try to get id by searching for the url first
        mon_id = target_monitor.get('id')
        if mon_id:
            mon_found = any(str(mon_id) == str(m['id']) for m in actual_monitors)
        else:
            match = next((m for m in actual_monitors if m['url'] == target_monitor['url']), None)
            if match:
                mon_id = match['id']
                mon_found = True
            else:
                mon_found = False

        # search the maintenance windows by friendly_name or ID
        # Build a mapping from friendly_name to id for quick lookup in actual_mwindows.
        friendly_to_mwin_id = {mwindow['friendly_name']: mwindow['id'] for mwindow in actual_mwindows}

        mwin_ids = []
        for target_mwindow in target_monitor.get('mwindows', []):
            # Use the mwindow's id if available; otherwise, look it up by friendly_name.
            mwin_id = target_mwindow.get('id') or friendly_to_mwin_id.get(target_mwindow['friendly_name'])
            if mwin_id:
                mwin_ids.append(str(mwin_id))

        target_monitor['api_key'] = args.API_KEY
        target_monitor['id'] = mon_id
        target_monitor['mwindows'] = '-'.join(mwin_ids)

        # search in alert_contacts by friendly_name or ID
        # Create a mapping from friendly_name to id for quick lookup.
        friendly_to_alert_id = {contact['friendly_name']: contact['id'] for contact in actual_alert_contacts}

        alert_ids = []
        for target_alert_contact in target_monitor.get('alert_contacts', []):
            # Use the alert contact's id if available; otherwise, use the mapping.
            alert_id = target_alert_contact.get('id') or friendly_to_alert_id.get(target_alert_contact['friendly_name'])
            if alert_id:
                alert_ids.append(f"{alert_id}_{target_alert_contact.get('threshold', 0)}_{target_alert_contact.get('recurrence', 0)}")

        target_monitor['api_key'] = args.API_KEY
        target_monitor['id'] = mon_id
        target_monitor['mwindows'] = '-'.join(mwin_ids)
        target_monitor['alert_contacts'] = '-'.join(alert_ids)

        # create
        if not mon_found and target_monitor.get('state', 'present') == 'present':
            print(f"Create Monitor `{target_monitor['friendly_name']}`... ", end='')
            success, result = lib.uptimerobot.new_monitor(target_monitor)
            print(f'{success}: {result}')
        # update
        if mon_found and target_monitor.get('state', 'present') == 'present':
            print(f"Update Monitor `{target_monitor['friendly_name']}`... ", end='')
            success, result = lib.uptimerobot.edit_monitor(target_monitor)
            print(f'{success}: {result}')
        # delete
        if mon_found and target_monitor.get('state', 'present') == 'absent':
            print(f"Delete Monitor `{target_monitor['friendly_name']}`... ", end='')
            target_monitor['id'] = int(mon_id)
            success, result = lib.uptimerobot.delete_monitor(target_monitor)
            print(f'{success}: {result}')

    return True


def apply_mwindows(args, targets):
    if not 'mwindows' in targets:
        return

    # get all mwindows from uptimerobot
    actual_mwindows = lib.base.coe(lib.uptimerobot.get_mwindows({
        'api_key': args.API_KEY,
    }))

    print(f'Working on {len(targets["mwindows"])} {lib.txt.pluralize("mwindow", len(targets["mwindows"]))}.')
    for target_mwindow in targets['mwindows']:
        # search for existing monitors
        # if given, use the id directly, otherwise try to get id by searching for
        # the friendly_name
        _id = target_mwindow.get('id')
        found = False
        for actual_mwindow in actual_mwindows:
            if not _id and target_mwindow['friendly_name'] == actual_mwindow['friendly_name']:
                _id = actual_mwindow['id']
                found = True
                break
            if _id and str(_id) == str(actual_mwindow['id']):
                found = True
                break

        target_mwindow['api_key'] = args.API_KEY
        target_mwindow['id'] = _id

        # create
        if not found and target_mwindow.get('state', 'present') == 'present':
            print(f"Create MWindow `{target_mwindow['friendly_name']}`... ", end='')
            success, result = lib.uptimerobot.new_mwindow(target_mwindow)
            print(f'{success}: {result}')
        # update
        if found and target_mwindow.get('state', 'present') == 'present':
            print(f"Update MWindow `{target_mwindow['friendly_name']}`... ", end='')
            success, result = lib.uptimerobot.edit_mwindow(target_mwindow)
            print(f'{success}: {result}')
        # delete
        if found and target_mwindow.get('state', 'present') == 'absent':
            print(f"Delete MWindow `{target_mwindow['friendly_name']}`... ", end='')
            target_mwindow['id'] = int(_id)
            success, result = lib.uptimerobot.delete_mwindow(target_mwindow)
            print(f'{success}: {result}')

    return True


def apply_alert_contacts(args, targets):
    if not 'alert_contacts' in targets:
        return

    # get all alert_contacts from uptimerobot
    actual_alert_contacts = lib.base.coe(lib.uptimerobot.get_alert_contacts({
        'api_key': args.API_KEY,
    }))

    print(f'Working on {len(targets["alert_contacts"])} {lib.txt.pluralize("alertcontact", len(targets["alert_contacts"]))}.')
    for target_alert_contact in targets['alert_contacts']:
        # search for existing monitors
        # if given, use the id directly, otherwise try to get id by searching for
        # the friendly_name
        _id = target_alert_contact.get('id')
        found = False
        for actual_alert_contact in actual_alert_contacts:
            if not _id and target_alert_contact['friendly_name'] == actual_alert_contact['friendly_name']:
                _id = actual_alert_contact['id']
                found = True
                break
            if _id and str(_id) == str(actual_alert_contact['id']):
                found = True
                break

        target_alert_contact['api_key'] = args.API_KEY
        target_alert_contact['id'] = _id

        # create
        if not found and target_alert_contact.get('state', 'present') == 'present':
            print("Won't create AlertContacts, the API is too limited here")
            print("(it can't create POST parameters, for example).")
        # update
        if found and target_alert_contact.get('state', 'present') == 'present':
            print("Won't apply updates to AlertContacts, the API is too limited here")
            print("(it deletes pre-defined POST parameters, and you can't set them via API,")
            print('for example).')
        # delete
        if found and target_alert_contact.get('state', 'present') == 'absent':
            print(f"Delete AlertContact `{_id}`... ", end='')
            target_alert_contact['id'] = int(_id)
            success, result = lib.uptimerobot.delete_alert_contact(target_alert_contact)
            print(f'{success}: {result}')

    return True


def apply_psps(args, targets):
    if not 'psps' in targets:
        return

    # get all data from uptimerobot
    actual_psps = lib.base.coe(lib.uptimerobot.get_psps({
        'api_key': args.API_KEY,
    }))
    actual_monitors = lib.base.coe(lib.uptimerobot.get_monitors({
        'api_key': args.API_KEY,
    }))

    print(f'Working on {len(targets["psps"])} {lib.txt.pluralize("psp", len(targets["psps"]))}.')
    for target_psp in targets['psps']:
        # search for existing psps
        # if given, use the id directly, otherwise try to get id by searching for the name first
        psp_id = target_psp.get('id')
        if psp_id:
            psp_found = any(str(psp_id) == str(p['id']) for p in actual_psps)
        else:
            match = next((p for p in actual_psps if p['friendly_name'] == target_psp['friendly_name']), None)
            if match:
                psp_id = match['id']
                psp_found = True
            else:
                psp_found = False

        # search the monitors by friendly_name or ID
        target_monitors = target_psp.get('monitors', [])

        # Build a mapping from friendly_name to id for quick lookup.
        friendly_to_id = {monitor['friendly_name']: monitor['id'] for monitor in actual_monitors}

        mon_ids = []
        for target_monitor in target_monitors:
            try:
                # Use the monitor's id if available; otherwise, look it up by friendly_name.
                mon_id = target_monitor.get('id') or friendly_to_id.get(target_monitor['friendly_name'])
                if mon_id:
                    mon_ids.append(str(mon_id))
            except:
                pass

        target_psp['api_key'] = args.API_KEY
        target_psp['id'] = psp_id
        target_psp['monitors'] = '-'.join(mon_ids)

        # create
        if not psp_found and target_psp.get('state', 'present') == 'present':
            print(f"Create Status Page `{target_psp['friendly_name']}`... ", end='')
            success, result = lib.uptimerobot.new_psp(target_psp)
            print(f'{success}: {result}')
        # update
        if psp_found and target_psp.get('state', 'present') == 'present':
            print(f"Update Status Page `{target_psp['friendly_name']}`... ", end='')
            success, result = lib.uptimerobot.edit_psp(target_psp)
            print(f'{success}: {result}')
        # delete
        if psp_found and target_psp.get('state', 'present') == 'absent':
            print(f"Delete Status Page `{target_psp['friendly_name']}`... ", end='')
            target_psp['id'] = int(psp_id)
            success, result = lib.uptimerobot.delete_psp(target_psp)
            print(f'{success}: {result}')

    return True


def set_monitors(args):
    params = args.field_filters
    params.update({
        'api_key': args.API_KEY,
    })
    monitors = lib.base.coe(lib.uptimerobot.get_monitors(params))

    print(f'Working on {len(monitors)} {lib.txt.pluralize("monitor", len(monitors))}.')
    for item in monitors:
        params.update({
            'id': item['id'],
        })
        print(f"Update Monitor `{item['friendly_name']}`... ", end='')
        success, result = lib.uptimerobot.edit_monitor(params)
        print(f'{success}: {result}')


def set_psps(args):
    params = args.field_filters
    params.update({
        'api_key': args.API_KEY,
    })
    psps = lib.base.coe(lib.uptimerobot.get_psps(params))

    print(f'Working on {len(psps)} {lib.txt.pluralize("psp", len(psps))}.')
    for item in psps:
        params.update({
            'id': item['id'],
        })
        print(f"Update Status Page `{item['friendly_name']}`... ", end='')
        success, result = lib.uptimerobot.edit_psp(params)
        print(f'{success}: {result}')


def main():
    """The main function. Hier spielt die Musik.
    """

    # parse the command line, exit with UNKNOWN if it fails
    try:
        args = parse_args()
        # get the API key for UptimeRobot
        if not args.API_KEY:
            args.API_KEY_FILE = args.API_KEY_FILE.replace('~', os.path.expanduser('~'))
            success, key = lib.disk.read_file(args.API_KEY_FILE)
            if success:
                args.API_KEY = key.strip()
    except SystemExit:
        sys.exit(3)
    if not args.API_KEY:
        lib.base.cu('API key missing. Use `--api_key` or provide `--api_key_file`.')

    # run a command
    if args.COMMAND == 'get' and args.RESOURCE == 'account':
        get_account_details(args)
    if args.COMMAND == 'get' and args.RESOURCE == 'alert_contacts':
        get_alert_contacts(args)
    if args.COMMAND == 'get' and args.RESOURCE == 'monitors':
        get_monitors(args)
    if args.COMMAND == 'get' and args.RESOURCE == 'mwindows':
        get_mwindows(args)
    if args.COMMAND == 'get' and args.RESOURCE == 'psps':
        get_psps(args)

    if args.COMMAND == 'apply':
        data = parse_and_preprocess_yaml(args)
        apply_alert_contacts(args, data)
        apply_mwindows(args, data)
        apply_monitors(args, data)
        apply_psps(args, data)

    if args.COMMAND == 'set' and args.RESOURCE == 'account':
        lib.base.oao('todo, not implemented yet')
    if args.COMMAND == 'set' and args.RESOURCE == 'alert_contacts':
        lib.base.oao('todo, not implemented yet')
    if args.COMMAND == 'set' and args.RESOURCE == 'monitors':
        set_monitors(args)
    if args.COMMAND == 'set' and args.RESOURCE == 'mwindows':
        lib.base.oao('todo, not implemented yet')
    if args.COMMAND == 'set' and args.RESOURCE == 'psps':
        set_psps(args)


if __name__ == '__main__':
    try:
        main()
    except Exception:   # pylint: disable=W0703
        lib.base.cu()
