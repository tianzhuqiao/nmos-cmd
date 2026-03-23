from .cmd import cli
from .utility import load_config

def main():
    cli(default_map=load_config())
