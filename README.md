# CheckDNS

CheckDNS is an application that can be used in a terminal. It gives the user the ability to look up domain names.

## Installing checkDNS

1. Pull the repo
2. Create a virtual environment inside the repo with `python3 -m venv <venv_name>`
3. Install requirements with `pip install -r requirements.txt`

## Basic usage checkDNS

To show all options for checkDNS, use:

```
python3 checkdns.py --help
```

Retrieving information about 1 domain is simple:

```
python3 checkdns.py --domain google.com
```

The terminal then outputs all retrieved information about this domain.

A more advanced example:

```
python3 checkdns.py --domain-list example.txt --export-json example.json
```

In this example `--domain-list` is used to specify the file to read the input domainnames from. This input file should be in the following format.

```
<domainname1>
<domainname2>
<domainname3>
...
```

`--export-json` is used to specify where the output should be saved. This file must be in `json` format. The exported `json` will have the following format.

```json
{
  "<domainname1>": {
    "whois": {},
    "host_ips": [],
    "mx_record": [],
    "txt_record": []
  },
  "<domainname2>": {
    "whois": {},
    "host_ips": [],
    "mx_record": [],
    "txt_record": []
  }
}
```

When stuck, try using `--help` to show all options and dont hesitate to explore your options.
