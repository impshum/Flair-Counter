import configparser
import praw
import pickledb
from collections import Counter
from halo import Halo


config = configparser.ConfigParser()
config.read('config.ini')
client_id = config.get('REDDIT', 'client_id')
client_secret = config.get('REDDIT', 'client_secret')
reddit_user = config.get('REDDIT', 'reddit_user')
reddit_pass = config.get('REDDIT', 'reddit_pass')
target_sub = config.get('SETTINGS', 'target_sub')
test_mode = int(config.get('TEST_MODE', 'test_mode'))

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent='Flair Analytics (by /u/impshum)',
                     username=reddit_user,
                     password=reddit_pass)

db = pickledb.load('data.db', False)

spinner = Halo(text='Booting up...', spinner='dots')
spinner.start()


def do_db(author, flair):
    if not db.exists(author):
        db.set(author, flair)
        db.dump()
        return True
    else:
        return False


def spin_text(text):
    spinner.text = text


def main():
    c = 0
    for submission in reddit.subreddit(target_sub).new(limit=None):
        if not submission.saved:
            if do_db(str(submission.author), submission.author_flair_text):
                c += 1
                spin_text(f'Found {c} users')
                if not test_mode:
                    submission.save()

        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            if not comment.saved:
                if do_db(str(comment.author), comment.author_flair_text):
                    c += 1
                    spin_text(f'Found {c} users')
                    if not test_mode:
                        comment.save()
    spinner.succeed()


def read():
    data = db.getall()
    all = []

    for x in data:
        all.append({'user': x, 'flair': db.get(x)})

    counted = Counter(k['flair'] for k in all if k.get('flair'))

    flaired_users = 0
    for flair, c in counted.items():
        flaired_users += c
        print(flair, c)

    total_users = len(data)
    print(f'{flaired_users}/{total_users} users have flairs')


if __name__ == '__main__':
    main()
    read()
