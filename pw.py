import pickle

import subprocess
import click
from simplekv.fs import FilesystemStore

__version__ = '0.1.0'
store = FilesystemStore('./store')


@click.command(context_settings={"ignore_unknown_options": True})
@click.version_option(version=__version__)
@click.argument('command', nargs=1)
@click.argument('args', nargs=-1)
@click.pass_context
def pw(ctx, command, args):
    """pw
    """
    if command in subcommands:
        if args:
            ctx.invoke(subcommands[command], alias=args[0], args=args[1:])
        else:
            ctx.invoke(subcommands[command])
    else:
        real_command = store.get(command)
        real_command = pickle.loads(real_command)
        subprocess.call(real_command)


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument('alias', nargs=1)
@click.argument('args', nargs=-1)
def add(alias, args):
    """add"""
    data = pickle.dumps(args)
    store.put(alias, data)


@click.command(name="list")
def list_all():
    """list"""
    print(store.keys())


@click.command()
def delete_all():
    """delete all"""
    for k in store.keys():
        store.delete(k)


subcommands = {
    'add': add,
    'list': list_all,
    'delete_all': delete_all,
}


if __name__ == '__main__':
    pw()
