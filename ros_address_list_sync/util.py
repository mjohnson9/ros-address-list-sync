import subprocess

import netaddr


def normalize_cidr(cidr):
    return str(netaddr.ip.IPNetwork(cidr))


def mikrotik_cidr(cidr):
    if cidr.endswith('/32'):
        cidr = cidr[:-3]

    return cidr


def retrieve_addr_with_port(addr):
    port = None
    port_location = addr.rfind(':')
    if port_location != -1:
        port = addr[port_location + 1:]
        addr = addr[:port_location]

    return netaddr.IPAddress(addr), port


def get_list_from_command(command):
    output = subprocess.check_output(command)
    addresses = set(map(lambda cidr: normalize_cidr(cidr), output.splitlines()))
    return addresses


def find_changes(desired_list, current_list):
    to_add = desired_list - current_list
    to_remove = current_list - desired_list

    return to_add, to_remove
