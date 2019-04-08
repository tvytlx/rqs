import enum
import fnmatch
import os
import pickle
import subprocess
from pathlib import Path

import click
import crayons
from simplekv.fs import FilesystemStore


VERSION = "0.1.7"
STORAGE_PATH = os.path.join(Path.home(), ".rqs_storage")

store = FilesystemStore(STORAGE_PATH)


class EntryType(enum.Enum):
    COMMAND = "command"
    VARIABLE = "variable"


class Entry:
    def __init__(self, alias, args):
        self.args = args
        self.content = " ".join(args)
        self.alias = alias
        if which(args[0]):
            self.type = EntryType.COMMAND
            self.emoji = '🔮'
        else:
            self.type = EntryType.VARIABLE
            self.emoji = '🔑'

    def execute(self):
        subprocess.call(self.args)

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

    A handy tool to keep your credentials or frequent used commands.

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
        $ rqs add mongo_login mongo localhost -u xxx -p xxx
        rqs added an command type entry.

    \b
        $ rqs mongo_local
        > (local) show dbs

    \b
        $ rqs add APIKEY xxxxxx
        rqs added an variable type entry.

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

            ctx.invoke(subcommands[command], alias=args[0], args=args[1:])
            return

        if command == "delete":
            if len(args) != 1:
                print(crayons.red("invalid argument"))
                exit(1)

            ctx.invoke(subcommands[command], key=args[0])
            return

        ctx.invoke(subcommands[command])
    else:  # treated as an entry
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


def add(alias, args):
    entry = Entry(alias, args)
    print(crayons.white(f"{entry.emoji} rqs added a {entry.type.value} entry.", bold=True))
    data = pickle.dumps(entry)
    store.put(alias, data)


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


def which(program):
    return not bool(
        subprocess.call(
            ["which", program], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    )


def delete(key):
    store.delete(key)
    print(crayons.white(f"🌚 rqs deleted {key}.", bold=True))


def delete_all():
    """delete all"""
    for k in store.keys():
        store.delete(k)


subcommands = {"add": add, "list": list_all, "delete": delete, "delete_all": delete_all}


if __name__ == "__main__":
    rqs()
