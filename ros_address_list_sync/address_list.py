class AddressList(object):
    def __init__(self, pairs):
        self.indexes = dict()
        self.cidrs = set()

        for index, address in pairs:
            indexSet = self.indexes.get(address)
            if indexSet is None:
                indexSet = set()
                self.indexes[address] = indexSet

            indexSet.add(index)
            self.cidrs.add(address)

    def get_indices(self, cidr):
        return self.indexes.get(cidr, None)
