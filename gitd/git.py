"""
Small wrapper around the Git command line
"""
import subprocess as sub
import os
import re
from functools import wraps


class GitException(Exception):
    pass


class Git(object):
    """
    Git Wrapper Object

    Note that all methods in this wrapper assume that you are in a
    git repository directory already.  Exceptions will be raised
    if the user is not.
    """
    def __init__(self):
        self.commit_regex = re.compile('(?:commit\s+)(.+)')
        self.branch_regex = re.compile('(?:\*\s+)(.+)')

    def show(self):
        """
        Execute show command
        """
        try:
            return sub.check_output(['git', 'show'])
        except sub.CalledProcessError as e:
            raise GitException('Git::Show: ' + e .message);

    def branch(self):
        """
        Return the branch of the current git repository
        """
        return self.branch_regex.findall(self.branch())[0]

    def commit_id(self):
        """
        Return the current commit id
        """
        return self.commit_regex.findall(self.show())[0]

    def pull(self):
        """
        Execute a pull command on the current repository
        """
        try:
            return sub.check_output(['git', 'pull'])
        except sub.CalledProcessError as e:
            raise GitException('Git::pull: ' + e.message)
