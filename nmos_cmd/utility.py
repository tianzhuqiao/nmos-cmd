from pathlib import Path
import functools
import json
import platformdirs
import click
import tqdm
from .version import PROJECT_NAME

def get_config_dir():
    config_dir = platformdirs.user_config_dir(PROJECT_NAME, "nmos-cmd team")
    return config_dir

def get_folder_in_config(folder):
    return Path(get_config_dir())/folder


def echo(*args, **kwargs):
    if not kwargs.get('tqdm_mode', False):
        click.secho(*args, **kwargs)
    else:
        end = '\n'
        if not kwargs.get('nl', True):
            end = ''
        kwargs.pop('nl', None)
        tqdm.tqdm.write(click.style(*args, **kwargs), end=end)

def info(*args, **kwargs):
    echo(*args, **kwargs)

def error(*args, **kwargs):
    if 'fg' not in kwargs:
        kwargs['fg'] = 'red'
    echo(*args, **kwargs)

def warning(*args, **kwargs):
    if 'fg' not in kwargs:
        kwargs['fg'] = 'blue'
    echo(*args, **kwargs)

def success(*args, **kwargs):
    if 'fg' not in kwargs:
        kwargs['fg'] = 'green'
    info(*args, **kwargs)

def load_config():
    cfg = {}
    filename = Path(get_config_dir())/f"{PROJECT_NAME}.ini"
    if filename.is_file():
        with open(filename, 'r', encoding='utf-8') as file:
            cfg = json.load(file)
    return cfg

def save_config(cfg):
    Path(get_config_dir()).mkdir(parents=True, exist_ok=True)
    filename = Path(get_config_dir())/f"{PROJECT_NAME}.ini"
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(cfg, file, indent=4)

def port_ver_option(port, ver, spec):
    def _common_options(f):
        options = []
        if spec == "is04":
            options = [
                    click.option(f'--{port}', default=3212, help='NMOS IS-04 port'),
                    click.option(f'--{ver}', default="1.2", type=click.Choice(['1.0', '1.1', '1.2', '1.3']),
                                 help='NMOS IS-04 version')
                    ]
        elif spec == "is05":
            options = [
                    click.option(f'--{port}', default=3215, help='NMOS IS-05 port'),
                    click.option(f'--{ver}', default="1.0", type=click.Choice(['1.0', '1.1', '1.2']),
                                 help='NMOS IS-05 version')
                    ]

        return functools.reduce(lambda x, opt: opt(x), reversed(options), f)
    return _common_options

def commom_patch_options():
    def _common_options(f):
        options = [click.option('--mode', default='immediate',
                                type=click.Choice(['immediate', 'scheduled_absolute', 'scheduled_relative']),
                                help='Activation mode'),
                   click.option('--requested_time', help='Requested time'),
                   click.option('--curl', is_flag=True, help='Print the corresponding curl command'),
                   click.option('--verbose', is_flag=True, help='Be verbose')
        ]

        return functools.reduce(lambda x, opt: opt(x), reversed(options), f)
    return _common_options

def other_patch_options():
    def _common_options(f):
        options = [click.option('--device', required=True,
                                help='device IP or IP@name'),
                   click.option('--stream', multiple=True, help='Stream to be enabled (id or label)')
                   ]
        return functools.reduce(lambda x, opt: opt(x), reversed(options), f)
    return _common_options
