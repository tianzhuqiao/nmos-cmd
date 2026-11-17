import click
from .utility import get_folder_in_config as _F
from .utility import port_ver_option, other_patch_options, commom_patch_options
from .nmos import NMOS

@click.group(name='receiver')
def rx():
    """
    Send NMOS PATCH/Bulk command to config receiver.

    e.g., to connect the sender streams to receiver streams.
    """

@rx.command(name="list", context_settings={'show_default': True})
@click.option('--device', required=True,
              help='Device IP@name or IP:port@name or IP:port:version@name')
@port_ver_option("port", "version", "is04")
@click.option('--stream', multiple=True, help='Stream to be shown')
@click.option('--output', type=click.Path(exists=True, dir_okay=False),
              help='If provided, save the configuration to a file')
def list_rx(device, port, version, stream, output):
    """
    Show the current configuration, or save it to a file.
    """
    n = NMOS()
    n.list_stream(device, port, version, stream, output, receiver=True)

@rx.command(name="config", context_settings={'show_default': True})
@click.option('--sender', required=True,
              help='sender device IP@name or IP:port@name or IP:port:version@name')
@port_ver_option("sender_port", "sender_version", "is04")
@click.option('--receiver', required=True,
              help='receiver device IP@name or IP:port@name or IP:port:version@name')
@port_ver_option("receiver_port", "receiver_version", "is04")
@click.option('--stream', default=["video:video"], multiple=True,
              help='the stream to be configured, in format: "sender stream":"receiver stream"')
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
@port_ver_option("port", "version", "is05")
@click.option('--bulk', is_flag=True, help='Send with single bulk command')
@commom_patch_options()
def apply_rx(cfg, port, version, mode, requested_time, master_enable, bulk, curl, verbose):
    """
    Apply the PATCH to the receiver streams defined in "--config".
    """
    n = NMOS(is05_ver=version, is05_port=port)
    n.apply_rx(cfg, mode, requested_time, master_enable, bulk=bulk, curl=curl, verbose=verbose)


@rx.command(name="enable", context_settings={'show_default': True})
@other_patch_options()
@port_ver_option("port_is04", "version_is04", "is04")
@port_ver_option("port_is05", "version_is05", "is05")
@commom_patch_options()
def enable_rx(device, port_is04, version_is04, port_is05, version_is05, mode,
              requested_time, stream, curl, verbose):
    """
    Enable receiver streams.
    """
    n = NMOS(is04_ver=version_is04, is04_port=port_is04, is05_ver=version_is05,
             is05_port=port_is05)
    n.enable_stream(device, mode, requested_time, stream, True, curl=curl,
                    verbose=verbose)

@rx.command(name="disable", context_settings={'show_default': True})
@other_patch_options()
@port_ver_option("port_is04", "version_is04", "is04")
@port_ver_option("port_is05", "version_is05", "is05")
@commom_patch_options()
def disable_rx(device, port_is04, version_is04, port_is05, version_is05, mode,
               requested_time, stream, curl, verbose):
    """
    Disable receiver streams.
    """
    n = NMOS(is04_ver=version_is04, is04_port=port_is04, is05_ver=version_is05,
             is05_port=port_is05)
    n.enable_stream(device, mode, requested_time, stream, False, curl=curl,
                    verbose=verbose)
