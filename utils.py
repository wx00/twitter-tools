#!/usr/bin/env python3

from argparse import ArgumentTypeError
import datetime
import pickle

from concurrent.futures import ThreadPoolExecutor

from openpyxl import Workbook
from twitter import TwitterError

# typing import
from typing import Callable, Iterable, List, Optional, TextIO, Union
from twitter import Api, User


_FILE_CACHE_MINUTES = 15


def static_vars(**kwargs):
    def decorate(func: Callable):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


@static_vars(_cache=None)
def get_own(api: Api) -> User:
    if get_own._cache:
        return get_own._cache
    data: User = api.VerifyCredentials(skip_status=True)
    get_own._cache = data
    return data


def get_own_id(api: Api) -> int:
    return get_own(api).id


def write_cache(filename: str, data):
    try:
        with open(filename, 'wb') as f:
            content = {
                'date': datetime.datetime.now(),
                'data': data,
            }
            pickle.dump(content, f, protocol=pickle.HIGHEST_PROTOCOL)
        return content
    except IOError:
        return None


def load_cache(filename: str):
    try:
        with open(filename, 'rb') as f:
            c = pickle.load(f)
            return c
    except IOError:
        return None


def save_list(filename: str, content: Iterable):
    with open(filename, mode='w', encoding='utf-8') as f:
        f.writelines(map(lambda c: f'{c}\n', content))


def str2bool(arg: Union[None, bool, str]) -> Union[None, bool]:
    if isinstance(arg, bool) or arg is None:
        return arg
    if arg.lower() in ('t', 'y', 'yes', 'true'):
        return True
    elif arg.lower() in ('f', 'n', 'no', 'false'):
        return False
    else:
        raise ArgumentTypeError('Boolean value expected.')


def yield_from_file(f: TextIO) -> Iterable[str]:
    while True:
        data = f.readline()
        if not data:
            break
        yield data


def confirm(message: str, default: Optional[bool] = None) -> bool:
    if default is None:
        t = input(message)
    else:
        if default:
            default_input = 'y'
        else:
            default_input = 'n'
        t = input(f'{message} [{default_input}]')
    if t == '' or t is None and default is not None:
        return bool(default)
    while t not in ('y', 'n'):
        t = input('Type y or n: ')
    return bool(t == 'y')


def ids_to_users(ids: Iterable, users: Iterable[User]) -> Iterable:
    return filter(lambda x: x.id in ids, users)


def users_to_ids(users: Iterable[User]) -> Iterable:
    return map(lambda x: x.id, users)


def remove_users(api: Api, user_ids: Iterable[User], unblock: Optional[bool] = None):
    if unblock is None:
        unblock = confirm(
            'Unblock users after removed from followers list?', default=True
        )

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
        for uid in user_ids:
            executor.submit(remove_follower, uid)
        executor.shutdown(wait=True)
    except (KeyboardInterrupt, SystemExit):
        cancelled = True
        print('Interrupted, exiting...')

    save_list('failed_blocking_ids.list', block_failed_ids)

    if unblock:
        save_list('failed_unblocking_ids.list', unblock_failed_ids)


def save_users(users: Iterable[User], file: str):
    wb = Workbook()
    ws = wb.active

    ws.append(['User Id', 'Screen Name', 'User Name', 'Profile URL'])
    for user in users:
        ws.append(
            [
                user.id_str,
                f'@{user.screen_name}',
                user.name,
                f'https://twitter.com/{user.screen_name}',
            ]
        )

    wb.save(file)


def cursor_call(method: Callable, **kwargs) -> List:
    cursor = -1
    ids = []
    while cursor != 0:
        cursor, _, data = method(cursor=cursor, **kwargs)
        ids += data
    return ids


def get_friends(api: Api, printing: Optional[bool] = True, **kwargs) -> List:
    if printing:
        print('Getting following list...')
    try:
        friends = cursor_call(api.GetFriendsPaged, **kwargs)
    except TwitterError as e:
        op = ''
        if 'screen_name' in kwargs:
            op = f' of user: {kwargs["screen_name"]}'
        print(f'Error getting friends{op}.\n{e}')
        return []
    if printing:
        print(f'You have {len(friends)} followings')
    return friends


def get_followers(api: Api, printing: Optional[bool] = True, **kwargs) -> List:
    if printing:
        print('Getting followers list')
    try:
        followers = cursor_call(api.GetFollowersPaged, **kwargs)
    except TwitterError as e:
        op = ''
        if 'screen_name' in kwargs:
            op = f' of user: {kwargs["screen_name"]}'
        print(f'Error getting followers{op}.\n{e}')
        return []
    if printing:
        print(f'You have {len(followers)} followers')
    return followers


def get_friend_ids(api: Api, printing: Optional[bool] = True, **kwargs) -> List:
    if printing:
        print('Getting following list...')

    screenname_flag: bool = 'screen_name' in kwargs
    if screenname_flag:
        _cache_fn = f'.friend_ids.{kwargs["screen_name"]}.cache'
    else:
        _cache_fn = f'.friend_ids.{get_own_id(api)}.cache'
    c = load_cache(_cache_fn)
    if not (
        c is None
        or (datetime.datetime.now() - c['date'])
        > datetime.timedelta(minutes=_FILE_CACHE_MINUTES)
    ):
        return c['data']

    try:
        friend_ids = cursor_call(api.GetFriendIDsPaged, **kwargs)
    except TwitterError as e:
        op = ''
        if screenname_flag:
            op = f' of user: {kwargs["screen_name"]}'
        print(f'Error getting friend ids{op}.\n{e}')
        return []
    if printing:
        print(f'You have {len(friend_ids)} followings')

    write_cache(_cache_fn, friend_ids)
    return friend_ids


def get_follower_ids(api: Api, printing: Optional[bool] = True, **kwargs) -> List:
    if printing:
        print('Getting followers list')

    screenname_flag: bool = 'screen_name' in kwargs
    if screenname_flag:
        _cache_fn = f'.follower_ids.{kwargs["screen_name"]}.cache'
    else:
        _cache_fn = f'.follower_ids.{get_own_id(api)}.cache'
    c = load_cache(_cache_fn)
    if not (
        c is None
        or (datetime.datetime.now() - c['date'])
        > datetime.timedelta(minutes=_FILE_CACHE_MINUTES)
    ):
        return c['data']

    try:
        follower_ids = cursor_call(api.GetFollowerIDsPaged, **kwargs)
    except TwitterError as e:
        op = ''
        if screenname_flag:
            op = f' of user: {kwargs["screen_name"]}'
        print(f'Error getting follower ids{op}.\n{e}')
        return []
    if printing:
        print(f'You have {len(follower_ids)} followers')
    write_cache(_cache_fn, follower_ids)
    return follower_ids
