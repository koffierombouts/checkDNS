import whois
import click
import socket
import dns.resolver
import json

from rich.pretty import pprint
from pathlib import Path

def dns_resolver(domain: str, type: str):
    """
    Function resolves information like MX or SPF records
    """
    return dns.resolver.resolve(domain, type)

def toStringDate(whois_entry, dates_string: str):
    """
    Function converts date objects in entry to strings
    """
    if dates_string in whois_entry:
        old_dates = whois_entry[dates_string]
        new_dates = []

        if type(old_dates) == list:
            for date in old_dates:
                new_dates.append(str(date))
            whois_entry[dates_string] = new_dates
        else:
            whois_entry[dates_string] = str(old_dates)
    
    return whois_entry

def retrieveDomainInfo(domain: str):
    """
    Function retrieves following information:
    - whois entry
    - host_ips
    - mx_record
    - txt_record
    """
    domain_entry = {}
    try:
        whois_entry = toStringDate(whois.whois(domain), "creation_date")
        if whois_entry["domain_name"] == None:
            return None
        whois_entry = toStringDate(whois_entry, "updated_date")
        whois_entry = toStringDate(whois_entry, "expiration_date")
        domain_entry.update({"whois": whois_entry})

        domain_entry.update({"host_ips": [ str(i[4][0]) for i in socket.getaddrinfo(domain, 80) ]})
        
        domain_entry.update({"mx_record": [str(entry.exchange) for entry in dns_resolver(domain, "MX")]})
        
        domain_entry.update({"txt_record": [str(entry) for entry in dns_resolver(domain, "txt")]})
    except socket.gaierror as e:
        pass
    except dns.resolver.NoAnswer as e:
        pass
    except Exception as e:
        click.echo(e)

    return {domain: domain_entry}

@click.command()
@click.option("--domain", "-d", help="Public information about the given domain will be looked up and retrieved.")
@click.option("--domain-list", "-dl", help="Public information about all the domains in the file will be looked up and retrieved.", type=click.Path(exists=True,file_okay=True, dir_okay=False, readable=True))
@click.option("--export-json", type=click.Path(dir_okay=False, path_type=Path), help="All retrieved information will be saved in de passed file. Results are saved in .json format.")
@click.option("--verbose", "-v", is_flag=True, help="The terminal outputs the result, even when the output is exported.")
def terminal(domain, domain_list, export_json, verbose):
    """
    Function interacts with the terminal.
    """
    data = {}

    if domain and domain_list:
        raise click.UsageError("You cannot use --domain and --domain-list at the same time.")

    if not export_json and domain_list:
        if not click.confirm("You didnt specify a file to export to, do you wish to continue?"):
            export_json = Path(click.prompt("Specify the filepath", type=Path))
    
    if export_json:
        if not export_json.suffix == ".json":
            raise click.UsageError("The results file must be .json")
        else:
            try:
                with open(export_json, "r") as file:
                    content = file.read()
                    
                    if content != "":
                        click.confirm(f"{export_json} contains data. Do you wish to overwrite this and continue?", abort=True)
            except FileNotFoundError:
                pass

    if domain:
        domain_entry = retrieveDomainInfo(domain)
        if domain_entry:
            data.update(domain_entry)
        else:
            click.echo(domain+" is not a valid domain")
    elif domain_list:
        domains = []
        with open(domain_list, "r") as file:
            for line in file:
                domains.append(line.strip())

        domains_amount = len(domains)
        for index, domain in enumerate(domains, 1):        
            domain_entry = retrieveDomainInfo(domain)

            if domain_entry:
                data.update(domain_entry)
                click.echo(f"[{index}/{domains_amount}]: {domain} retrieved ...")
            else:
                click.echo(f"[{index}/{domains_amount}]: {domain}  is an invalid domain ...")
    
    if export_json:
        with open(export_json, "w") as file:
            json.dump(data, file)
            click.echo(f"Written succesfully to {export_json}")
    
    if verbose or not export_json:
        pprint(data)
    

if __name__ == "__main__":
    terminal()