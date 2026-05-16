# nmos-patch
**nmos-cmd** is a tool to make it easier to send [NMOS](https://specs.amwa.tv/nmos/) requests.


## Installation
```
$ pip install nmos-cmd
```
## Usage
To start from terminal
```
$ nmos-cmd --help
Usage: nmos-cmd [OPTIONS] COMMAND [ARGS]...

  A tool to connect the NMOS sender streams to receiver streams.

Options:
  --help  Show this message and exit.

Commands:
  config    Set default option for each command/subcommand.
  list      List streams of a device.
  receiver  Send NMOS PATCH/Bulk command to config receiver.
```

List all the senders/receivers from a device (e.g., to check the label of each streams)
```
$ nmos-cmd list --device xx.xx.xx.xx
```

Dump the current receiver configuration to a file (default only the streams with "video" in its label)
```
$ nmos-cmd receiver dump --device xx.xx.xx.xx --output config.json
```

To generate a configuration file to connect a sender to a receiver. For the **--stream** argument
- **--stream "A:B"**: connect the sender stream with "A" in its label to the receiver stream with "B" in its label.
- **--stream "A 1\~8:B 1\~8"**: connect the sender stream with "A 1" in its label to the receiver stream with "B 1" in its label; connect the sender stream with "A 2" in its label to the receiver stream with "B 2" in its label ...
```
$ nmos-cmd receiver config --sender "xx.xx.xx.xx@sender label" --receiver "xx.xx.xx.xx@receiver label" --stream "video:video" --stream "audio 1~8:udio 1~8" --output config.json
```

Apply the configuration to the receiver

```
$ nmos-cmd receiver apply --config config.json
```
