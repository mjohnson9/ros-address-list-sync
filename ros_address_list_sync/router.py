import routeros_api

from ros_address_list_sync import address_list
from ros_address_list_sync import util


class Router(object):
    """High-level API for interacting with a RouterOS router
    """
    def __init__(self, host, username, password, api_port=8728):
        self.router_api_pool = routeros_api.RouterOsApiPool(host, username, password, api_port)
        self.router_api = self.router_api_pool.get_api()
        self.address_list = self.router_api.get_resource('/ip/firewall/address-list')
        self.connection_list = self.router_api.get_resource('/ip/firewall/connection')

    def disconnect(self):
        self.router_api_pool.disconnect()

    def get_address_list(self, name):
        returned_items = self.address_list.call('print', arguments={'.proplist': '.id,address'}, queries={'list': name})
        address_set = list(map(lambda item: (item['id'], util.normalize_cidr(item['address'])), returned_items))
        addresses = address_list.AddressList(address_set)
        return addresses

    def get_connection_list(self):
        returned_items = self.connection_list.call('print', arguments={'.proplist': '.id,src-address,dst-address,reply-src-address,reply-dst-address'})
        return returned_items

    def add_address_list_entry(self, name, address):
        self.address_list.call('add', arguments={'list': name, 'address': address})

    def remove_address_list_entries(self, indices):
        self.address_list.call('remove', arguments={'numbers': ','.join(indices)})

    def remove_connections(self, connections):
        self.connection_list.call('remove', arguments={'numbers': ','.join(connections)})
