"""Representation of a git repository
"""
import subprocess as sub
import re
from functools import wraps
import os
from exc import RepoError


def goto_git_repo(f):
    """Decorator to go to and return from a git repository to execute a command.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        self = args[0]
        start_dir = os.getcwd()
        os.chdir(self.folder)
        rtn = f(*args, **kwargs)
        os.chdir(start_dir)
        return rtn
    return wrapper


class Repo:
    def __init__(self, folder, target_branch):
        """Constructor
        """
        
        # Should I have it automatically change branches?
        # self.branch = conf_dict['branch']

        # self.folder = conf_dict['repo_folder']
        self.folder = folder
        self.target_branch
        # Checking that the given repo_folder exists
        if not os.path.exists(conf_dict['repo_folder']):
            raise RepoError('Repository folder: ' + conf_dict['repo_folder'] \
                + ', does not exist')
    
        sd = os.getcwd()  # Start directory
        os.chdir(self.folder)
        try:
            p = sub.check_call(['git', 'status'], stdout=sub.PIPE, stderr=sub.PIPE)
        except sub.CalledProcessError:
            raise RepoError('Folder: ' + self.folder + ' is not a git repository')
        finally:
            os.chdir(sd)
        
        self.commit_regex = re.compile('(?:commit\s+)(.+)')
        self.branch_regex = re.compile('(?:\*\s+)(.+)')
        self.num_msgs = 0

    @property
    def commit(self):
        """Current commit
        """
        try:
            return self.commit_regex.findall(self.show())[0]
        except IndexError:
            raise RepoError('Regex for commit failed')

    @property
    @goto_git_repo
    def current_branch(self):
        """Get the current branch of the repository.
        """
        try:
            output = sub.check_output(['git', 'branch'])
            branch = self.branch_regex.findall(output)[0]
        except sub.CalledProcessError as e:
            raise RepoError(e.message)
        except IndexError:
            raise RepoError('Regex for branch failed')
        return branch

    @goto_git_repo
    def show(self):
        """Executes 'git show' and returns the output, raises a RepoError if an error is
        encountered while running the command.
        """
        try:
            output = sub.check_output(['git', 'show'])
        except sub.CalledProcessError as e:
            raise RepoError('GitRepo::show: ' + e.message)
        return output
    
    @goto_git_repo
    def pull(self):
        """Execute a 'git pull' command.
        """
        try:
            output = sub.check_output(['git', 'pull'])
        except sub.CalledProcessError as e:
            raise RepoError('GitRepo::pull: ' + e.message)
        return output
