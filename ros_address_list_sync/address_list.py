class AddressList(object):
    """Represents a firewall address list on a RouterOS device

    Attributes:
        cidrs (list[str]): All of the CIDRs within this address list
    """
    def __init__(self, pairs):
        """Initializes the address list

        Args:
            pairs ((str, str)): The (index, cidr) pairs to initialize this address
            list with
        """
        self._indexes = dict()
        self.cidrs = set()

        for index, address in pairs:
            indexSet = self._indexes.get(address)
            if indexSet is None:
                indexSet = set()
                self._indexes[address] = indexSet

            indexSet.add(index)
            self.cidrs.add(address)

    def get_indices(self, cidr):
        """Fetches the index(es) of a given CIDR

        Args:
            cidr (str): The CIDR to look up

        Returns:
            list[str]: Indexes of the given CIDR
        """
        return self._indexes.get(cidr, None)
