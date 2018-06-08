
# communicate with API
import praw

# config files
import json

# url handler
import urllib.request  # todo check if these are correct
import urllib.parse



user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"


import hashlib
import pickle
from collections import deque
import random
import os


import errno, os
import sys

# Sadly, Python fails to provide the following magic number for us.
ERROR_INVALID_NAME = 123
'''
Windows-specific error code indicating an invalid pathname.

See Also
----------
https://msdn.microsoft.com/en-us/library/windows/desktop/ms681382%28v=vs.85%29.aspx
    Official listing of all such codes.
'''

def is_pathname_valid(pathname: str) -> bool:
    '''
    `True` if the passed pathname is a valid pathname for the current OS;
    `False` otherwise.
    '''
    # If this pathname is either not a string or is but is empty, this pathname
    # is invalid.
    try:
        if not isinstance(pathname, str) or not pathname:
            return False

        # Strip this pathname's Windows-specific drive specifier (e.g., `C:\`)
        # if any. Since Windows prohibits path components from containing `:`
        # characters, failing to strip this `:`-suffixed prefix would
        # erroneously invalidate all valid absolute Windows pathnames.
        _, pathname = os.path.splitdrive(pathname)

        # Directory guaranteed to exist. If the current OS is Windows, this is
        # the drive to which Windows was installed (e.g., the "%HOMEDRIVE%"
        # environment variable); else, the typical root directory.
        root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
            if sys.platform == 'win32' else os.path.sep
        assert os.path.isdir(root_dirname)   # ...Murphy and her ironclad Law

        # Append a path separator to this directory if needed.
        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

        # Test whether each path component split from this pathname is valid or
        # not, ignoring non-existent and non-readable path components.
        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)
            # If an OS-specific exception is raised, its error code
            # indicates whether this pathname is valid or not. Unless this
            # is the case, this exception implies an ignorable kernel or
            # filesystem complaint (e.g., path not found or inaccessible).
            #
            # Only the following exceptions indicate invalid pathnames:
            #
            # * Instances of the Windows-specific "WindowsError" class
            #   defining the "winerror" attribute whose value is
            #   "ERROR_INVALID_NAME". Under Windows, "winerror" is more
            #   fine-grained and hence useful than the generic "errno"
            #   attribute. When a too-long pathname is passed, for example,
            #   "errno" is "ENOENT" (i.e., no such file or directory) rather
            #   than "ENAMETOOLONG" (i.e., file name too long).
            # * Instances of the cross-platform "OSError" class defining the
            #   generic "errno" attribute whose value is either:
            #   * Under most POSIX-compatible OSes, "ENAMETOOLONG".
            #   * Under some edge-case OSes (e.g., SunOS, *BSD), "ERANGE".
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == ERROR_INVALID_NAME:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    # If a "TypeError" exception was raised, it almost certainly has the
    # error message "embedded NUL character" indicating an invalid pathname.
    except TypeError as exc:
        return False
    # If no exception was raised, all path components and hence this
    # pathname itself are valid. (Praise be to the curmudgeonly python.)
    else:
        return True
    # If any other exception was raised, this is an unrelated fatal issue
    # (e.g., a bug). Permit this exception to unwind the call stack.
    #
    # Did we mention this should be shipped with Python already?

class RedditData:
    client_id = ""
    secret = ""
    redirect_uri = ""
    user_agent = ""


def initialize():
    with open('botconfig.json') as data_file:
        config_file = json.load(data_file)

    RedditData.client_id = config_file["reddit"]["client_id"]
    RedditData.secret = config_file["reddit"]["secret"]
    RedditData.redirect_uri = config_file["reddit"]["redirect_uri"]
    RedditData.user_agent = config_file["reddit"]["user_agent"]

def createSuperSub():
    with open("sublist.json") as data_file:
        configData = json.load(data_file)
    combinedSubname = "\'"
    for i in configData["subs"]:
        combinedSubname += (i["name"]) + "+"
    combinedSubname = combinedSubname[:-1]
    combinedSubname += '\''
    return combinedSubname


def CreateHash(filename):
    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    print("MD5: {0}".format(md5.hexdigest()))
    return md5

def GetPicsFromReddit(subs, picLimit):
    print("Fetching " + str(picLimit) + " pictures from " + subs)

    try:
        with open("images.p", "rb") as handle:
            alreadyPosted = pickle.load(handle)
    except:
        somehash = hashlib.md5(str(random.getrandbits(256)).encode('utf-8'))
        alreadyPosted = deque(somehash.hexdigest(), 100)

    submissions = reddit.subreddit(subs).hot(limit = 10)

    numberOfPicsFound = 0
    for submission in submissions:

        filename = "testpics\\" + submission.url.split('/')[-1]

        myopener = urllib.request.build_opener()
        myopener.addheaders = [('User-Agent', user_agent)]
        urllib.request.install_opener(myopener)
        if not is_pathname_valid(filename):
            break
        urllib.request.urlretrieve(submission.url, filename)


        md5 = CreateHash(filename)
        if md5.hexdigest() not in  alreadyPosted:
            alreadyPosted.append(md5.hexdigest())
            print("New picture found: " + submission.title)
            numberOfPicsFound = numberOfPicsFound + 1
        else:
            print("Among the last 100 pictures..")
            os.remove(filename)

        if numberOfPicsFound == picLimit:
            break

    if numberOfPicsFound != picLimit:
        print("Only found " + str(numberOfPicsFound) + " pictures.")
        # let the caller know especially if 0

    with open("images.p", "wb") as handle:
        pickle.dump(alreadyPosted, handle)

initialize()
reddit = praw.Reddit(client_id=RedditData.client_id,
                     client_secret=RedditData.secret,
                     redirect_uri=RedditData.redirect_uri,
                     user_agent=RedditData.user_agent)

print(reddit.read_only)  # Output: True

# continued from code above

GetPicsFromReddit("ImaginaryBestOf", 5)







# Output: 10 submission