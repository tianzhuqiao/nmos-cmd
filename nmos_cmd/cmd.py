import json
import click
from auto_click_auto import enable_click_shell_completion
from auto_click_auto.utils import detect_shell
from .utility import info, load_config, save_config
from .nmos import NMOS
from .rx import rx
from .version import PROJECT_NAME

@click.group()
def cli():
    """
    A tool to connect the NMOS sender streams to receiver streams.
    """

@cli.command(name="list", context_settings={'show_default': True})
@click.option('--device', required=True, help='the device IP')
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


@click.command()
def shell_completion():
    """Activate shell completion."""
    enable_click_shell_completion(
        program_name=PROJECT_NAME,
        verbose=True
    )

try:
    # if not supported, detect_shell will throw an exception
    detect_shell()
    config.add_command(shell_completion)
except:
    pass

cli.add_command(rx)
