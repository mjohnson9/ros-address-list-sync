import argparse
import logging

import netaddr

from ros_address_list_sync import router
from ros_address_list_sync import util


def main():
    """The entry point for the synchronization application."""
    logging.basicConfig(format='%(message)s', level=logging.ERROR)

    parser = argparse.ArgumentParser(description='synchronize an address list to a RouterOS device')
    parser.add_argument('--simplify', action='store_true', help='whether or not to simplify the address list')
    parser.add_argument('--reset-conntrack', action='store_true', help='whether or not to reset conntrack entries for modified IP addresses')
    parser.add_argument('--verbose', action='store_true', help='enable verbose messages')
    parser.add_argument('--debug', action='store_true', help='enable debug messages')
    parser.add_argument('router_address', metavar='host', type=str, help='the hostname of the router to which this list should be synchronized')
    parser.add_argument('router_username', metavar='user', type=str, help='the username to log in to the router with')
    parser.add_argument('router_password', metavar='password', type=str, help='the password to log in to the router with')
    parser.add_argument('router_list', metavar='list-name', type=str, help='the name of the address list to synchronize')
    parser.add_argument('list_generator', metavar='list-generator', type=str, help='the command to run to receive the desired list of addresses')

    args = parser.parse_args()

    if args.debug:
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        #root_logger.setFormat('%(filename)s:%(lineno)d %(message)s')
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    logger = logging.getLogger('main')

    logger.debug('connecting to router...')
    router_api = router.Router(args.router_address, args.router_username, args.router_password)

    logger.debug('running specified list generator command')
    desired_list = util.get_list_from_command(args.list_generator)
    logger.debug('retrieving list from router')
    current_list = router_api.get_address_list(args.router_list)

    if args.simplify:
        desired_set = netaddr.ip.sets.IPSet(desired_list)  # merges all of the CIDRs
        desired_list = set(map(lambda cidr: str(cidr), desired_set.iter_cidrs()))

    logger.debug('calculating differences')
    to_add, to_remove = util.find_changes(desired_list, current_list.cidrs)

    changed_address = netaddr.ip.sets.IPSet()

    entries_to_remove = set()

    for item in to_remove:
        item_indices = current_list.get_indices(item)
        entries_to_remove.update(item_indices)

        changed_address.add(item)

        logger.debug("removed %s", item)

    if len(entries_to_remove) > 0:
        router_api.remove_address_list_entries(entries_to_remove)

    for item in to_add:
        router_api.add_address_list_entry(args.router_list, item)

        changed_address.add(item)

        logger.debug("added %s", item)

    if args.reset_conntrack:
        connections_to_remove = set()

        connections = router_api.get_connection_list()
        for connection in connections:
            src_address, _ = util.retrieve_addr_with_port(connection['src-address'])
            dst_address, _ = util.retrieve_addr_with_port(connection['dst-address'])
            reply_src_address, _ = util.retrieve_addr_with_port(connection['reply-src-address'])
            reply_dst_address, _ = util.retrieve_addr_with_port(connection['reply-dst-address'])

            if src_address in changed_address or dst_address in changed_address or reply_src_address in changed_address or reply_dst_address in changed_address:
                connections_to_remove.add(connection['id'])

                logger.debug('removed connection %s<->%s', reply_src_address, reply_dst_address)

        if len(connections_to_remove) > 0:
            router_api.remove_connections(connections_to_remove)
            #logging.debug('removed %d connections', len(connections_to_remove))

    #returned_items = self.address_list.call('print', arguments={'.proplist': 'address'}, queries={'list': name})

    logger.debug('disconnecting')
    router_api.disconnect()
    logger.debug('disconnected')

if __name__ == "__main__":
    main()
