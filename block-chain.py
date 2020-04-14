#!/usr/bin/env python3
import argparse
from queue import Queue

import common
from utils import (
    confirm,
    get_followers,
    get_friend_ids,
    get_follower_ids,
    get_own_id,
    str2bool,
    remove_users,
    users_to_ids,
    save_list,
    yield_from_file,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    user_source = parser.add_mutually_exclusive_group()
    user_source.add_argument(
        '--screenname', '-u', help='Username(w/o @) to start block chain.'
    )
    user_source.add_argument(
        '--from-file',
        '-f',
        metavar='FILE',
        type=argparse.FileType(encoding='utf-8'),
        help='Use usernames in text file. One user per line.',
    )
    user_source.add_argument(
        '--from-ids',
        '-i',
        metavar='FILE',
        type=argparse.FileType(encoding='utf-8'),
        help='Block ids in text file. One id per line.',
    )
    parser.add_argument(
        '--levels', '-l', metavar='N', type=int, help='Levels to block.'
    )
    parser.add_argument(
        '--exclude-followers',
        '-x',
        metavar='TRUE|FALSE',
        type=str2bool,
        help='Exclude own followers when blocking users. '
        'Users you following are already excluded.',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Generate user ids to block, but don't actually block them. You can save ids",
    )
    args = parser.parse_args()

    api = common.api()

    curQ = Queue()
    ids_to_block = set()

    if args.screenname:
        curQ.put(str(args.screenname).strip())
    elif args.from_file:
        with open(args.from_file, 'r') as f:
            for name in yield_from_file(f):
                curQ.put(name.strip())
    elif args.from_ids:
        with open(args.from_ids, 'r') as f:
            for uid in yield_from_file(f):
                ids_to_block.add(int(uid))
            args.levels = 0
    else:
        curQ.put(input("Input username to start block-chain: @"))

    if args.levels is not None:
        chain_depth = args.levels
    else:
        chain_depth = input("Levels to block?(default: 1): ")
    if chain_depth == '':
        chain_depth = 1
    else:
        chain_depth = int(chain_depth)

    if args.exclude_followers is None:
        exclude_followers = confirm('Exclude followers?', default=True)
    else:
        exclude_followers = args.exclude_followers

    own_id = get_own_id(api)
    friends_set = set(get_friend_ids(api))
    if exclude_followers:
        friends_set |= set(get_follower_ids(api))
    friends_set.add(own_id)

    for _1 in range(chain_depth):
        for _2 in range(curQ.qsize()):
            curUser = curQ.get()
            curUserFoers = get_followers(api, printing=False, screen_name=curUser)
            users_to_block = list(
                filter(
                    lambda x: x.id not in friends_set and x.id not in ids_to_block,
                    curUserFoers,
                )
            )
            if len(users_to_block) == 0:
                continue
            ids_to_block |= set(users_to_ids(users_to_block))
            for u in users_to_block:
                curQ.put(u.screen_name)

    ids_to_block -= friends_set
    if args.dry_run:
        print(f'Number of users to block: {len(ids_to_block)}.')
        if confirm('Save list of user-ids-to-block?', default=False):
            save_list(f'user_ids_to_block-{own_id}.list', ids_to_block)
        exit(0)
    remove_users(api, ids_to_block, unblock=False)
