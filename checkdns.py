import whois
import click
import socket
import dns.resolver
import json

from rich.pretty import pprint

def dns_resolver(domain: str, type: str):
    return dns.resolver.resolve(domain, type)

def retrieveDomainInfo(domain: str):
    domain_entry = {}
    try:
        def toStringDate(whois_entry, dates_string: str):
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
        print(e)

    return {domain: domain_entry}

@click.command()
@click.option("--domain", "-d", help="Public information about the given domain will be looked up and retrieved.")
@click.option("--read-file", "-r", help="Public information about all the domains in the file will be looked up and retrieved.", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option("--write-file", "-w", help="All retrieved information will be saved in de passed file. Results are saved in .json format. If no file is given, it will save to results.json", type=click.Path(dir_okay=False), default="results.json")
def terminal(domain, read_file, write_file):
    data = {}
    if domain and read_file:
        raise click.UsageError("You cannot use --domain and --read_file at the same time.")
    elif domain:
        domain_entry = retrieveDomainInfo(domain)
        if domain_entry:
            data.update(domain_entry)
            pprint(data)
        else:
            print(domain+" is not a valid domain")
    elif read_file:
        domains = []
        with open(read_file, "r") as file:
            for line in file:
                domains.append(line.strip())

        domains_amount = len(domains)
        for index, domain in enumerate(domains, 1):        
            domain_entry = retrieveDomainInfo(domain)

            if domain_entry:
                data.update(domain_entry)
                print(f"[{index}/{domains_amount}]: {domain} retrieved ...")
            else:
                print(f"[{index}/{domains_amount}]: {domain}  is an invalid domain ...")
    
        pprint(data)

if __name__ == "__main__":
    terminal()