import enum
import fnmatch
import os
import pickle
import subprocess
from pathlib import Path

import click
import crayons
from simplekv.fs import FilesystemStore


VERSION = "0.3.0"
STORAGE_PATH = os.path.join(Path.home(), ".rqs_storage")

store = FilesystemStore(STORAGE_PATH)


class EntryType(enum.Enum):
    COMMAND = "command"
    TEXT = "text"


class Entry:
    def __init__(self, alias, args_content):
        if not isinstance(args_content, (list, tuple)):
            raise ValueError

        self.alias = alias
        self.content = ' '.join(args_content)
        if is_valid_command(args_content[0]):
            self.type = EntryType.COMMAND
            self.emoji = '🔮'
        else:
            self.type = EntryType.TEXT
            self.emoji = '🔑'

    def execute(self):
        if self.type != EntryType.COMMAND:
            raise ValueError(f"{self.type.value} type entry can't be executed.")

        subprocess.call(self.content)

    def __str__(self):
        if self.type == EntryType.COMMAND:
            connector = "->"
            color = crayons.green
        else:
            connector = "="
            color = crayons.yellow

        return f"{color(self.alias, bold=True)} {color(connector)} {self.content}"


@click.command(context_settings={"ignore_unknown_options": True})
@click.version_option(version=VERSION)
@click.argument("command", nargs=1)
@click.argument("args", nargs=-1)
@click.pass_context
def rqs(ctx, command, args):
    """

    A handy tool to manage your credentials or frequent used commands.

    \b
    COMMAND:
        add ENTRT_NAME other_command    # add an entry
        list                            # list all entries
        delete ENTRY_NAME               # delete entry by name
        delete_all                      # delete all entries

    \b
    RUN ENTRY:
        rqs ENTRY_NAME

    \b
    EXAMPLES:

    \b
        $ rqs add mongo_local mongo localhost -u xxx -p xxx
        rqs added a command entry.

    \b
        $ rqs mongo_local
        > (local) show dbs

    \b
        $ rqs add APIKEY xxxxxx
        rqs added a text entry.

    \b
        $ rqs APIKEY  # just print APIKEY to stdout
        xxxxxx
    """
    if command in subcommands:  # treated as rqs command
        if command == "add":
            # invalid args, like: rqs add xx
            if not args or len(args) == 1:
                print(crayons.red("invalid argument"))
                exit(1)
            ctx.invoke(subcommands[command], alias=args[0], entry_content=args[1:])
            return

        if command == "delete":
            if len(args) != 1:
                print(crayons.red("invalid argument"))
                exit(1)

            ctx.invoke(subcommands[command], key=args[0])
            return

        ctx.invoke(subcommands[command])
    else:  # treated as an existed entry
        matches = fnmatch.filter(store.keys(), command)
        if len(matches) > 1:
            print_entries(matches)
            return
        if not matches:
            print(crayons.yellow(f"rqs has no entry for {command}"))
            return

        entry = pickle.loads(store.get(matches[0]))

        if entry.type == EntryType.COMMAND:
            entry.execute()
        else:
            print(entry.content)


def add(alias, entry_content):
    entry = Entry(alias, entry_content)
    data = pickle.dumps(entry)
    store.put(alias, data)
    print(crayons.white(f"{entry.emoji} rqs added a {entry.type.value} entry.", bold=True))


def list_all():
    print_entries(store.keys())


def print_entries(keys):
    print(crayons.white("Entries:", bold=True))
    if not keys:
        print("empty")
    entries = [pickle.loads(store.get(key)) for key in keys]
    entries.sort(key=lambda x: (x.type.value, x.alias), reverse=True)
    for entry in entries:
        print("\t" + str(entry))


def is_valid_command(program):
    """ Invoke `which` command in shell to check if the command is valid."""
    return not bool(
        subprocess.call(
            ["which", program], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    )


def delete(key):
    try:
        store.get(key)
    except KeyError:
        print(crayons.yellow(f"rqs has no entry for {key}"))
        return

    store.delete(key)
    print(crayons.white(f"🌚 rqs deleted {key}.", bold=True))


def delete_all():
    """delete all"""
    if input("Are you sure? y/n\n") not in ('y', ''):
        return

    for k in store.keys():
        store.delete(k)
    print(crayons.white(f"🌚 rqs deleted all entries.", bold=True))


subcommands = {"add": add, "ls": list_all, "list": list_all, "del": delete, "delete": delete, "delete_all": delete_all}


if __name__ == "__main__":
    rqs()
