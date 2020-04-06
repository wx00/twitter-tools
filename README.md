# Twitter tools

## Usage

- To backup friends list, execute `friends_backup.py` and follow instructions.

- To remove followers, execute `followers_clear.py` and follow instructions.

- To remove all following and followers, execute `nuke_friends_followers.py` and follow instructions.

- To block someone's followers chain, execute `block-chain.py` and follow instructions.
Use `block-chain.py --help` to see help message.

- From upstream: `nuke_like_archive.py` and `nuke_tweet_archive.py` are also available.


## Dependencies

Requires Python 3.6+(because I like f-strings)

Main dependencies are:

- python-twitter
- openpyxl
- pyyaml

Run `pip3 install -r requirements.txt` to install dependencies.

## Notes

Consumer keys can be found [here](https://gist.github.com/mariotaku/5465786). Use these keys instead of applying yourself can get rid of rate limit.

## TODOs

User filtering(used in follower removal section):

- Protected
- Following-follower ratio
- Following-follower difference
- Date registered
- Date of last tweet
- Other??
