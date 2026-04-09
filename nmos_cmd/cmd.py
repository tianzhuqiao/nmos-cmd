import os
import re
from pathlib import Path
import json
import requests
import click
from .utility import get_folder_in_config as _F
from .utility import success, error, warning, info, load_config, save_config


class NMOS:

    def __init__(self, is04_ver=None, is04_port=None, is05_ver=None, is05_port=None):
        cfg = load_config()
        self.cfg = {'timeout': 30,
                    'is04_ver': '1.2',
                    'is04_port': 3212,
                    'is05_ver': '1.0',
                    'is05_port': 3215}
        if "main" in cfg:
            self.cfg.update(cfg['main'])
        self.timeout = self._set_with_default(30, self.cfg['timeout'])
        self.is04_ver = self._set_with_default(is04_ver, self.cfg['is04_ver'])
        self.is04_port = self._set_with_default(is04_port, self.cfg['is04_port'])
        self.is05_ver = self._set_with_default(is05_ver, self.cfg['is05_ver'])
        self.is05_port = self._set_with_default(is05_port, self.cfg['is05_port'])

    def _set_with_default(self, value, default=None):
        if value is not None:
            return value
        return default

    def get_is04_url(self, device):
        """
        Generate the IS04 url (node) for device
        """
        return f"http://{device}:{self.is04_port}/x-nmos/node/v{self.is04_ver}"

    def get_is05_url(self, device):
        """
        Generate the IS05 url (connection) for device
        """
        return f"http://{device}:{self.is05_port}/x-nmos/connection/v{self.is05_ver}"

    def get_receiver(self, device, receiver):
        """
        Return the receiver streams of "device" filtered by the name in "receiver"

        The output is the dictionary: {stream label: stream id}
        """
        result = {}
        res = requests.get(f"{self.get_is04_url(device)}/devices/", timeout=self.timeout)
        d = res.json()
        if isinstance(receiver, str):
            receiver = [receiver]
        for dd in d:
            for rid in dd["receivers"]:
                r = requests.get(f"{self.get_is04_url(device)}/receivers/{rid}",
                                 timeout=self.timeout)
                r = r.json()
                if not receiver or all(rec in r["label"] for rec in receiver):
                    result[r['label']] = r['id']

        return result

    def get_sender(self, device, sender, download=False):
        """
        Return the sender streams of "device" filtered by the name in "sender"

        The output is the dictionary: {stream label: stream id}, ant it will also
        download the corresponding sdp to be used by the receiver streams.
        """
        result = {}
        res = requests.get(f"{self.get_is04_url(device)}/devices/", timeout=self.timeout)
        d = res.json()
        if isinstance(sender, str):
            sender = [sender]
        for dd in d:
            for sid in dd["senders"]:
                r = requests.get(f"{self.get_is04_url(device)}/senders/{sid}", timeout=self.timeout)
                r = r.json()
                if not sender or all(rec in r["label"] for rec in sender):
                    result[r['label']] = r['id']
                    if download:
                        self.download_sdp(r['manifest_href'], _F(device), r['id'])

        return result

    def download_sdp(self, url, folder, filename=""):
        """
        Download the sdp file from url to folder/filename.
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            # Raise an exception for bad status codes (4XX or 5XX)
            response.raise_for_status()
            if not filename:
                filename = Path(url).name
            os.makedirs(folder, exist_ok=True)
            with open(Path(folder)/filename, 'wb') as file:
                file.write(response.content)
        except requests.exceptions.RequestException as e:
            error(f"Download '{url}' failed: {e}")


    def list_device(self, device, receiver, sender):
        """
        List the sender and receiver streams from device
        """
        res = requests.get(f"{self.get_is04_url(device)}/devices/", timeout=self.timeout)
        d = res.json()
        os.makedirs(_F(device), exist_ok=True)
        for dd in d:
            info(dd["description"])
            for rid in dd["receivers"]:
                r = requests.get(f"{self.get_is04_url(device)}/receivers/{rid}",
                                 timeout=self.timeout)
                r = r.json()
                if not receiver or all(rx in r["label"] for rx in receiver):
                    info(f"    {r['label']} {r['id']}")
            for sid in dd["senders"]:
                r = requests.get(f"{self.get_is04_url(device)}/senders/{sid}", timeout=self.timeout)
                r = r.json()
                if not sender or all(tx in r["label"] for tx in sender):
                    info(f"    {r['label']} {r['id']} {r['manifest_href']}")

    def _parse_device(self, device, port, ver):
        """
        Parse the device, supported format IP@name or IP:port@name or IP:port:version@name

        If port/version is defined in "device", it will take priority.
        """
        ip, name = device.split('@')
        ip = ip.split(':')
        if port is None:
            port = self.is04_port
        if ver is None:
            ver = self.is04_ver
        if len(ip) == 1:
            ip = ip[0]
        elif len(ip) == 2:
            ip, port = ip
        elif len(ip) == 3:
            ip, port, ver = ip
        return ip, port, ver, name

    def _expand_streams(self, stream):
        stream2 = []
        for s in stream:
            expanded = False
            s2 = s.split(":")
            if len(s2) != 2:
                warning(f"Invalid stream: {s}")
                continue
            tx = re.findall(r"\d?~\d?", s2[0])
            rx = re.findall(r"\d?~\d?", s2[1])
            if len(rx) == 1 and len(tx) == 1 and tx == rx:
                # expand "audio output 1~8:audio input 1~8" to
                # audio output 1:audio input 1
                # audio output 1:audio input 2
                # ...
                # audio output 1:audio input 8
                rng = tx[0].split("~")
                if len(rng) == 2 and rng[0].isnumeric() and rng[1].isnumeric():
                    for idx in range(int(rng[0]), int(rng[1]) + 1):
                        stream2.append(s.replace(tx[0], str(idx)))
                    expanded = True

            if not expanded:
                stream2.append(s)
            return stream2

    def generate_patch(self, sender, sender_port, sender_version, receiver,
                       receiver_port, receiver_version, stream, output):
        """
        Generate the config json file to connect the receiver streams to the
        corresponding sender streams.
        """
        info("Get sender streams")
        tx_ip, tx_port, tx_ver, tx_name = self._parse_device(sender, sender_port, sender_version)
        tx_d = NMOS(is04_port=tx_port, is04_ver=tx_ver)
        tx = tx_d.get_sender(tx_ip, tx_name, True)

        info("Get receiver streams")
        rx_ip, rx_port, rx_ver, rx_name = self._parse_device(receiver, receiver_port,
                                                             receiver_version)
        rx_d = NMOS(is04_port=rx_port, is04_ver=rx_ver)
        rx = rx_d.get_receiver(rx_ip, rx_name)
        mapping = []
        info("Connect sender streams to receiver streams")
        for s in self._expand_streams(stream):
            s = s.split(":")
            if len(s) == 1:
                s = [s, s]
            # find the tx stream
            s_tx = [ r for r in tx if s[0] in r]
            if len(s_tx) != 1:
                error(f"Multiple or no streams found in sender for '{s[0]}'!")
                return
            s_tx = s_tx[0]

            # find the rx stream
            s_rx = [ r for r in rx if s[1] in r]
            if len(s_rx) != 1:
                error(f"Multiple or no streams found in receiver '{s[1]}'!")
                return
            s_rx = s_rx[0]

            with open(Path(_F(tx_ip))/tx[s_tx], 'r', encoding='utf-8') as file:
                sdp = file.read()
                mapping.append([rx_ip, s_rx, rx[s_rx], sdp])

        # save the patch configuration
        p = Path(output)
        if not p.suffix:
            p = p.with_suffix('.json')

        if p.is_file():
            if not click.confirm(f"'{p}' exists; would you like to overwrite it?", default=False):
                return
        info(f"Save the config to {p}")
        with open(p, "w", encoding='utf-8') as json_file:
            json.dump(mapping, json_file, indent=4)

    def apply_patch(self, cfg, mode, requested_time):
        """
        Sent the PATCH command one by one defined in the configuration json file.
        """
        if mode not in ['immediate', 'scheduled_absolute', 'scheduled_relative']:
            error(f"Unknown activation mode: {mode}")
            return
        if mode == 'immediate':
            requested_time = None
        elif not re.match(r'^[0-9]+:[0-9]+$', requested_time):
            error(f"Unknown requested time: {requested_time}")
            return

        with open(cfg, 'r', encoding='utf-8') as file:
            cfg = json.load(file)
            for c in cfg:
                device, rx_name, rx, sdp = c
                data = {"activation":{"mode": f"activate_{mode}",
                                      "requested_time": requested_time
                                      },
                        "transport_file": {"data": "\r\n".join(sdp.lstrip().split('\n')),
                                           "type": "application/sdp"
                                           }
                        }

                url = f'{self.get_is05_url(device)}/single/receivers/{rx}/staged'
                response = requests.patch(url, json=data, timeout=self.timeout)
                if response.status_code != 200:
                    error(f"Patch '{rx_name}' failed: {response.status_code}")
                    error(f"    {url}")
                else:
                    success(f"Patch '{rx_name}' succeeded: {response.status_code}")

@click.group()
def cli():
    """
    A tool to connect the NMOS sender streams to receiver streams.
    """

@cli.command(name="list", context_settings={'show_default': True})
@click.option('--device', help='the device IP')
@click.option('--port', default=3212, help='NMOS IS04 port')
@click.option('--version', default="1.2", type=click.Choice(['1.0', '1.1', '1.2', '1.3']),
              help='NMOS IS04 version')
@click.option('--receiver', multiple=True, help='only show the receiver streams with specific name')
@click.option('--sender', multiple=True, help='only show the sender streams with specific name')
def list_device(device, port, version, receiver, sender):
    """
    List streams of a device.
    """
    n = NMOS(is04_ver=version, is04_port=port)
    n.list_device(device, receiver, sender)

@cli.group()
def patch():
    """
    Send NMOS PATCH command.

    e.g., to connect the sender streams to receiver streams.
    """

@patch.command(name="config", context_settings={'show_default': True})
@click.option('--sender', help='sender device IP@name or IP:port@name or IP:port:version@name')
@click.option('--sender_port', default=3212, help='NMOS IS04 port')
@click.option('--sender_version', default="1.2", type=click.Choice(['1.0', '1.1', '1.2', '1.3']),
              help='NMOS IS04 version')
@click.option('--receiver', help='receiver device IP@name or IP:port@name or IP:port:version@name')
@click.option('--receiver_port', default=3212, help='NMOS IS04 port')
@click.option('--receiver_version', default="1.2", type=click.Choice(['1.0', '1.1', '1.2', '1.3']),
              help='NMOS IS04 version')
@click.option('--stream', default=["video:video"],
              multiple=True, help='the stream to be configured, in format "sender stream"@"receiver stream"')
@click.option('--output', help='the output patch configuration filename')
def generate_patch(sender, sender_port, sender_version, receiver, receiver_port,
                   receiver_version, stream, output):
    """
    Generate the configuration file to connect the sender streams to the receiver streams.
    """
    n = NMOS()
    n.generate_patch(sender, sender_port, sender_version, receiver, receiver_port,
                     receiver_version, stream, output)

@patch.command(name="apply", context_settings={'show_default': True})
@click.option('--config', 'cfg',  default="config.json", help='the patch configuration file')
@click.option('--port', default=3215, help='NMOS IS05 port')
@click.option('--version', default='1.0', type=click.Choice(['1.0', '1.1']),
              help='NMOS IS05 version')
@click.option('--mode', default='immediate',
              type=click.Choice(['immediate', 'scheduled_absolute', 'scheduled_relative']),
              help='Activation mode')
@click.option('--requested_time', help='Requested time')
def apply_patch(cfg, port, version, mode, requested_time):
    """
    Apply the PATCH to the receiver streams defined in "--config".
    """
    n = NMOS(is05_ver=version, is05_port=port)
    n.apply_patch(cfg, mode, requested_time)

@cli.group(name="config", context_settings={'show_default': True})
def config():
    """
    Set default option for each command/subcommand.
    """

@config.command(name="set", context_settings={'show_default': True})
@click.argument('key')
@click.argument('value')
def config_set(key, value):
    """
    Set default option for each command.

    For example, the following command will set the default port for "list" command to 3213

       nmos-patch config set list.port 3213
    """

    cfg = load_config()
    t = cfg
    for k in key.split('.')[:-1]:
        if k not in cfg:
            t[k] = {}
        t = t[k]
    t[key.split('.')[-1]] = value
    save_config(cfg)

@config.command(name="list", context_settings={'show_default': True})
def config_list():
    """
    List all the default options
    """
    cfg = load_config()
    info(json.dumps(cfg, indent=4))
