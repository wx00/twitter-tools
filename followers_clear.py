#!/usr/bin/env python3
from common import api
from utils import get_friend_ids, get_follower_ids, remove_users


if __name__ == "__main__":
    friend_ids = get_friend_ids(api)
    follower_ids = get_follower_ids(api)

    no_mutual_followers = set(follower_ids) - set(friend_ids)

    print(f'You have {len(no_mutual_followers)} followers you haven\'t followed.')


    test_rm_list = [8084062, 3999403878, 3799859959, 19274281]
    remove_users(api, test_rm_list)
