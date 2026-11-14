from pathlib import Path
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

def ask_yes_no(question: str) -> bool:
    while True:
        answer = input(f"{question} (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Invalid input. Please enter 'y' or 'n'.")
