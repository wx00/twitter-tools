#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor

from openpyxl import Workbook
from twitter import TwitterError


def confirm(message, default=None):
    if default is None:
        t = input(message)
    else:
        if default:
            default_input = 'y'
        else:
            default_input = 'n'
        t = input('%s [%s]' % (message, default_input))
    if t == '' or t is None and default is not None:
        return bool(default)
    while t not in ('y', 'n'):
        t = input('Type y or n: ')
    return bool(t == 'y')


def ids_to_users(ids, users):
    return list(filter(lambda x: x.id in ids, users))


def users_to_ids(users):
    return list(map(lambda x: x.id, users))


def remove_users(api, user_ids):
    unblock = confirm('Unblock users after removed?', default=True)

    executor = ThreadPoolExecutor(max_workers=80)

    cancelled = False

    block_failed_ids = []
    unblock_failed_ids = []

    def remove_follower(uid):
        if cancelled:
            return
        try:
            print(f'blocking {uid}')
            api.CreateBlock(uid)
        except TwitterError:
            block_failed_ids.append(uid)
        if unblock:
            try:
                print(f'unblocking {uid}')
                api.DestroyBlock(uid)
            except TwitterError:
                unblock_failed_ids.append(uid)

    try:
        for user_id in user_ids:
            executor.submit(remove_follower, user_id)
        executor.shutdown(wait=True)
    except (KeyboardInterrupt, SystemExit):
        cancelled = True
        print('Interrupted, exiting...')

    with open('failed_blocking_ids.list', 'w') as f:
        for user_id in block_failed_ids:
            f.write(f'{user_id}\n')

    with open('failed_unblocking_ids.list', 'w') as f:
        for user_id in unblock_failed_ids:
            f.write(f'{user_id}\n')


def save_users(users, file):
    wb = Workbook()
    ws = wb.active

    ws.append(['User Id', 'Screen Name', 'User Name', 'Profile URL'])
    for user in users:
        ws.append([user.id_str, f'@{user.screen_name}', user.name,
                   f'https://twitter.com/{user.screen_name}'])

    wb.save(file)


def cursor_call(method):
    cursor = -1
    ids = []
    while cursor != 0:
        cursor, _, data = method(cursor=cursor)
        ids += data
    return ids


def get_friends(api):
    print('Getting following list...')
    friends = cursor_call(api.GetFriendsPaged)
    print(f'You have {len(friends)} followings')
    return friends


def get_followers(api):
    print('Getting followers list')
    followers = cursor_call(api.GetFollowersPaged)
    print(f'You have {len(followers)} followers')
    return followers


def get_friend_ids(api):
    print('Getting following list...')
    friend_ids = cursor_call(api.GetFriendIDsPaged)
    print(f'You have {len(friend_ids)} followings')
    return friend_ids


def get_follower_ids(api):
    print('Getting followers list')
    follower_ids = cursor_call(api.GetFollowerIDsPaged)
    print(f'You have {len(follower_ids)} followers')
    return follower_ids
