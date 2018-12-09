#!/usr/bin/env python3

from common import api, confirm
from utils import get_friends, get_followers, save_users


def backup_friends(api, file='friends.xlsx'):
    save_users(get_friends(api), file)


def backup_followers(api, file='followers.xlsx'):
    save_users(get_followers(api), file)



if __name__ == "__main__":
    if confirm('Save friends list?[Y/n]', default=True):
        backup_friends(api)

    if confirm('Save followers list?[Y/n]', default=True):
        backup_followers(api)
