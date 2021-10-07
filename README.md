Purpose
=======

This project contains the Python API client to interact with the Cornèr Bank data transfer platform.

Installation
============

To install the client, run the following command:


```python
make install
```

If you don't have `make` installed, you can also run:

```python
pip install -r requirements.txt
```

Usage
=====

The usage is quite simple:

```
usage: corner-data-transfer.py [-h] -u USERNAME -p PASSWORD [--url URL] {latest,list,list-unread,download} ...

Cornèr Bank data transfer client.

positional arguments:
  {latest,list,list-unread,download}
    latest                            get the latest / newest file
    list                              list all files
    list-unread                       list unread files
    download                          download (and decrypt) a file

optional arguments:
  -h, --help                          show this help message and exit
  -u USERNAME, --username USERNAME    the username
  -p PASSWORD, --password PASSWORD    the password
  --url URL                           the base URL
```

For example, if you want to list the files you can run:

```bash
corner-data-transfer.py -u ${USERNAME} -p ${PASSWORD} list
```

To download a file you can run:

```bash
corner-data-transfer.py -u ${USERNAME} -p ${PASSWORD} download testfile.txt.pgp  /tmp/testfile.txt
```

The file will automatically be decrypted by GPG. If you don't want that, you can use the `-n` CLI flag after the `download` command.
