import click
from .utility import get_folder_in_config as _F
from .nmos import NMOS

@click.group(name='receiver')
def rx():
    """
    Send NMOS PATCH/Bulk command to config receiver.

    e.g., to connect the sender streams to receiver streams.
    """

@rx.command(name="dump", context_settings={'show_default': True})
@click.option('--device', required=True,
              help='receiver device IP@name or IP:port@name or IP:port:version@name')
@click.option('--port', default=3212, help='NMOS IS04 port')
@click.option('--version', default="1.2", type=click.Choice(['1.0', '1.1', '1.2', '1.3']),
              help='NMOS IS04 version')
@click.option('--stream', default=["video"],
              multiple=True, help='the stream to be dumped')
@click.option('--output', default="config.json", type=click.Path(exists=True, dir_okay=False),
              help='the output configuration filename')
def dump_rx(device, port, version, stream, output):
    """
    Dump the current configuration to a file.
    """
    n = NMOS()
    n.dump_rx(device, port, version, stream, output)

@rx.command(name="config", context_settings={'show_default': True})
@click.option('--sender', required=True,
              help='sender device IP@name or IP:port@name or IP:port:version@name')
@click.option('--sender_port', default=3212, help='NMOS IS04 port')
@click.option('--sender_version', default="1.2", type=click.Choice(['1.0', '1.1', '1.2', '1.3']),
              help='NMOS IS04 version')
@click.option('--receiver', required=True,
              help='receiver device IP@name or IP:port@name or IP:port:version@name')
@click.option('--receiver_port', default=3212, help='NMOS IS04 port')
@click.option('--receiver_version', default="1.2", type=click.Choice(['1.0', '1.1', '1.2', '1.3']),
              help='NMOS IS04 version')
@click.option('--stream', default=["video:video"], multiple=True,
              help='the stream to be configured, in format "sender stream"@"receiver stream"')
@click.option('--output', default="config.json", type=click.Path(exists=False, dir_okay=False),
              help='the output patch configuration filename')
def config_rx(sender, sender_port, sender_version, receiver, receiver_port,
                   receiver_version, stream, output):
    """
    Generate the configuration file to connect the sender streams to the receiver streams.
    """
    n = NMOS()
    n.config_rx(sender, sender_port, sender_version, receiver, receiver_port,
                     receiver_version, stream, output)

@rx.command(name="apply", context_settings={'show_default': True})
@click.option('--config', 'cfg', default="config.json",
              type=click.Path(exists=True, dir_okay=False),
              help='the patch configuration file')
@click.option('--port', default=3215, help='NMOS IS05 port')
@click.option('--version', default='1.0', type=click.Choice(['1.0', '1.1']),
              help='NMOS IS05 version')
@click.option('--mode', default='immediate',
              type=click.Choice(['immediate', 'scheduled_absolute', 'scheduled_relative']),
              help='Activation mode')
@click.option('--requested_time', help='Requested time')
@click.option('--bulk', is_flag=True, help='Send with single bulk command')
def apply_rx(cfg, port, version, mode, requested_time, bulk):
    """
    Apply the PATCH to the receiver streams defined in "--config".
    """
    n = NMOS(is05_ver=version, is05_port=port)
    n.apply_rx(cfg, mode, requested_time, bulk)
