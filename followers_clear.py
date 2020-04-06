#!/usr/bin/env python3
import common
from utils import get_friend_ids, get_follower_ids, remove_users


if __name__ == "__main__":
    api = common.api()
    friend_ids = get_friend_ids(api)
    follower_ids = get_follower_ids(api)

    no_mutual_followers = set(follower_ids) - set(friend_ids)

    print(f'You have {len(no_mutual_followers)} followers you haven\'t followed.')


    remove_users(api, no_mutual_followers)
