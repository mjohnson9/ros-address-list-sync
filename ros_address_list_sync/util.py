import subprocess

import netaddr


def normalize_cidr(cidr):
    """Normalizes a CIDR into our internal format

    Args:
        cidr (str): The CIDR to normalize

    Returns:
        str: The normalized CIDR
    """
    return str(netaddr.ip.IPNetwork(cidr))


def mikrotik_cidr(cidr):
    """Normalizes a CIDR into Mikrotik format

    Args:
        cidr (str): The CIDR to normalize

    Returns:
        str: The CIDR normalized into Mikrotik format
    """
    cidr = normalize_cidr(cidr)

    if cidr.endswith('/32'):
        cidr = cidr[:-3]

    return cidr


def retrieve_addr_with_port(addr):
    """Retrieves an IP address and port from a string containing both in typical format

    Args:
        addr (str): The IP:port combination to extract from

    Returns:
        (netaddr.IPAddress, int): The IP address and port number
    """
    port = None
    port_location = addr.rfind(':')
    if port_location != -1:
        port = addr[port_location + 1:]
        addr = addr[:port_location]

    return netaddr.IPAddress(addr), port


def get_list_from_command(command):
    """Runs a command and returns the output as a list of CIDRs

    Args:
        command (str): The command to run

    Returns:
        list[str]: Normalized CIDRs
    """
    output = subprocess.check_output(command)
    addresses = set(map(lambda cidr: normalize_cidr(cidr), output.splitlines()))
    return addresses


def find_changes(desired_list, current_list):
    """Finds the necessary changes to make current_list match desired_list

    Args:
        desired_list (set[str]): The desired list of items
        current_list (set[str]): The current list of items

    Returns:
        (set[str], set[str]): The items that must be added and remove, respectively, to make the sets match
    """
    to_add = desired_list - current_list
    to_remove = current_list - desired_list

    return to_add, to_remove
