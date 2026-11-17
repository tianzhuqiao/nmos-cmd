import click
from .utility import get_folder_in_config as _F
from .utility import port_ver_option, other_patch_options, commom_patch_options
from .nmos import NMOS

@click.group(name='sender')
def tx():
    """
    Send NMOS PATCH/Bulk command to config sender.

    e.g., to enable/disable sender streams.
    """

@tx.command(name="list", context_settings={'show_default': True})
@click.option('--device', required=True,
              help='Device IP@name or IP:port@name or IP:port:version@name')
@port_ver_option("port", "version", "is04")
@click.option('--stream', multiple=True, help='Stream to be shown')
@click.option('--output', type=click.Path(exists=True, dir_okay=False),
              help='If provided, save the configuration to a file')
def list_tx(device, port, version, stream, output):
    """
    Show the current configuration, or save it to a file.
    """
    n = NMOS()
    n.list_stream(device, port, version, stream, output, receiver=False)

@tx.command(name="enable", context_settings={'show_default': True})
@other_patch_options()
@port_ver_option("port_is04", "version_is04", "is04")
@port_ver_option("port_is05", "version_is05", "is05")
@commom_patch_options()
def enable_tx(device, port_is04, version_is04, port_is05, version_is05, mode,
              requested_time, stream, curl, verbose):
    """
    Enable sender streams.
    """
    n = NMOS(is04_ver=version_is04, is04_port=port_is04, is05_ver=version_is05, is05_port=port_is05)
    n.enable_stream(device, mode, requested_time, stream, True, curl=curl,
                    verbose=verbose, receiver=False)

@tx.command(name="disable", context_settings={'show_default': True})
@other_patch_options()
@port_ver_option("port_is04", "version_is04", "is04")
@port_ver_option("port_is05", "version_is05", "is05")
@commom_patch_options()
def disable_tx(device, port_is04, version_is04, port_is05, version_is05, mode,
               requested_time, stream, curl, verbose):
    """
    Disable sender streams.
    """
    n = NMOS(is04_ver=version_is04, is04_port=port_is04, is05_ver=version_is05,
             is05_port=port_is05)
    n.enable_stream(device, mode, requested_time, stream, False, curl=curl,
                    verbose=verbose, receiver=False)
