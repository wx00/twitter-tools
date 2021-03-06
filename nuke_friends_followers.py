#!/usr/bin/env python3
import common

from common import api
from utils import get_friend_ids, get_follower_ids, remove_users


if __name__ == "__main__":
    api = common.api()
    friend_ids = get_friend_ids(api)
    follower_ids = get_follower_ids(api)

    ids_to_delete = set(follower_ids) | set(friend_ids)

    print(f'You have {len(ids_to_delete)} followers/friends in total.')

    remove_users(api, ids_to_delete)
