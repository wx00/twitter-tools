# Twitter relation removal tool

## Usage

- To backup friends list, execute `friends_backup.py` and choose what to backup.

- To remove followers, execute `followers_clear.py` and follow instructions.

- To remove all following and followers, execute `all_clear.py` and follow instructions.

## Dependencies

This variant requires Python 3.6+(because I like f-strings)

Main dependencies are::

- python-twitter
- openpyxl
- pyyaml

Execute `pip3 install -r requirements.txt` to install dependencies

## Notes

Consumer keys can be found [here](https://gist.github.com/mariotaku/5465786). Use these keys instead of applying yourself can get rid of rate limit.

## TODOs

User filtering(only used in follower removal script):

- Protected
- Following-follower ratio
- Following-follower difference
- Date registered
- Other??
