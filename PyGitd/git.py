import subprocess as sub
import os
import re
from functools import wraps


class GitRepoError(Exception):
    pass


def goto_git_repo(f):
    """
    Decorator to go to and return from a git repository to execute a command.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        self = args[0]
        start_dir = os.getcwd()
        os.chdir(self.repo_folder)
        rtn = f(*args, **kwargs)
        os.chdir(start_dir)
        return rtn
    return wrapper


class GitRepo(object):
    def __init__(self, repo_folder):
        self.repo_folder = repo_folder
        
        # Verifying that the folder exists
        if not os.path.exists(repo_folder):
            raise GitRepoError('Repository : ' + repo_folder + ' does not exist')
        
        start_dir = os.getcwd()
        os.chdir(repo_folder)
        # Verifying that the given folder is a Git repository
        p = sub.Popen(['git', 'status'], stdout=sub.PIPE, stderr=sub.PIPE)
        p.wait()

        os.chdir(start_dir)
        
        if p.returncode != 0:
            raise GitRepoError('Folder : ' + repo_folder + ' is not a git repository')

        self.commit_regex = re.compile('(?:commit\s+)(.+)')
        self.branch_regex = re.compile('(:?\*\s+)(.+)')

    @property
    def commit(self):
        return self.commit_regex.findall(self.show())[0]

    @property
    @goto_git_repo
    def branch(self):
        try:
            output = sub.check_output(['git', 'branch'])
            branch = self.branch_regex.findall(output)[0]
        except sub.CalledProcessError as e:
            raise GitRepoError(e.message)
        except IndexError:
            raise GitRepoError('Regex for branch failed')
        return branch

    @goto_git_repo
    def show(self):
        """
        Executes 'git show' and returns the output, raises a GitRepoError if an error is
        encountered while running the command.
        """
        try:
            output = sub.check_output(['git', 'show'])
        except sub.CalledProcessError as e:
            raise GitRepoError('GitRepo::show: ' + e.message)
        return output
    
    @goto_git_repo
    def pull(self):
        try:
            output = sub.check_output(['git', 'pull'])
        except sub.CalledProcessError as e:
            raise GitRepoError('GitRepo::pull: ' + e.message)
        return output    
