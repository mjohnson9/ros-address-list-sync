import routeros_api

from ros_address_list_sync import address_list
from ros_address_list_sync import util


class Router(object):
    """High-level API for interacting with a RouterOS router
    """
    def __init__(self, host, username, password, api_port=8728):
        """Initialize the connection to the RouterOS device

        Args:
            host (str): The hostname of the device to initialize the connection to
            username (str): The username to log in to the device with
            password (str): The password to log in to the device with
            api_port (int, optional): The API port of the device
        """
        self._router_api_pool = routeros_api.RouterOsApiPool(host, username, password, api_port)
        self._router_api = self._router_api_pool.get_api()
        self._address_list = self.router_api.get_resource('/ip/firewall/address-list')
        self._connection_list = self.router_api.get_resource('/ip/firewall/connection')

    def disconnect(self):
        """Disconnect from the RouterOS device
        """
        self._router_api_pool.disconnect()

    def get_address_list(self, name):
        """Retrieve an address list from the RouterOS device

        Args:
            name (str): Name of the address list

        Returns:
            ros_address_list_sync.address_list.AddressList: The retrieved address list
        """
        returned_items = self._address_list.call('print', arguments={'.proplist': '.id,address'}, queries={'list': name})
        address_set = list(map(lambda item: (item['id'], util.normalize_cidr(item['address'])), returned_items))
        addresses = address_list.AddressList(address_set)
        return addresses

    def add_address_list_entry(self, name, address):
        """Adds an address list entry to the RouterOS device

        Args:
            name (str): Name of the address list to add to
            address (str): CIDR to add to the address list
        """
        self._address_list.call('add', arguments={'list': name, 'address': address})

    def remove_address_list_entries(self, indices):
        """Removes a list of address list entries from the RouterOS device

        Args:
            indices (list[str]): List of the indices to remove
        """
        self._address_list.call('remove', arguments={'numbers': ','.join(indices)})

    def get_connection_list(self):
        """Retrieves all connections from the router's connection tracking table

        Returns:
            list[dict[str, str]]: The tracked connections
        """
        returned_items = self._connection_list.call('print', arguments={'.proplist': '.id,src-address,dst-address,reply-src-address,reply-dst-address'})
        return returned_items

    def remove_connections(self, connections):
        """Removes a list of connections from the device's connection tracking
        table

        Args:
            connections (list[str]): List of the indices of connections to remove
        """
        self._connection_list.call('remove', arguments={'numbers': ','.join(connections)})
