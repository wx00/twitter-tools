#!/usr/bin/env python3
from common import api, confirm
from utils import get_friends, get_followers, save_users


if __name__ == "__main__":
    if confirm('Save friends list?', default=True):
        save_users(get_friends(api), 'friends.xlsx')

    if confirm('Save followers list?', default=True):
        save_users(get_followers(api), 'followers.xlsx')
