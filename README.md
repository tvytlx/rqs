# rqs

A handy tool to manage your credentials or frequent used commands.


Usage
========

```
$ rqs --help
Usage: rqs [OPTIONS] COMMAND [ARGS]...

  A handy tool to manage your credentials or frequent used commands.

  COMMAND:
      add ENTRT_NAME other_command    # add an entry
      list                            # list all entries
      delete ENTRY_NAME               # delete entry by name
      delete_all                      # delete all entries

  RUN ENTRY:
      rqs ENTRY_NAME

  EXAMPLES:

      $ rqs add mongo_login mongo localhost -u xxx -p xxx
      rqs added an command type entry.

      $ rqs mongo_local
      > (local) show dbs

      $ rqs add APIKEY xxxxxx
      rqs added an variable type entry.

      $ rqs APIKEY  # just print APIKEY to stdout
      xxxxxx

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.
```

Install
========
```
$ pip install rqs
```