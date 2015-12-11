import imaplib
import smtplib
import time
import re
import logging
import traceback

from repo import Repo


class ManagerError(Exception):
    """
    Exception thrown when the manager encounters an error
    """
    pass


class NotificationError(Exception):
    """
    Error thrown by the Manager.notify() method when and error is
    encountered
    """
    pass


class Manager(object):
    def __init__(self, config):
        # Configuring Logging
        formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(ch)
        self.logger.setLevel(logging.INFO)
        
        # GIT Repositories
        self.repos = [Repo(repo_config) for repo_config in config['repos']]
        self.branch_regex = re.compile('(?:.+Branch:\s+)(.+)')
        self.commit_regex = re.compile('(?:.+Commit:\s+)(.+)')

        try:
            # General Information
            self.notifiees = config['notification_recipients']
            self.interval = config['interval']
            self.email = config['email']

            # IMAP Connection
            self.logger.info('Initializing connection to IMAP server : ' + config['imap_server'])
            self.mail = imaplib.IMAP4_SSL(config['imap_server'])
            self.mail.login(config['email'], config['password'])
            self.logger.info('Connection established to IMAP server : ' + config['imap_server'])

            # SMTP Connection
            self.logger.info('Initializing connection to SMTP server : ' + config['smtp_server'])
            self.smtp = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            self.smtp.starttls()
            self.smtp.login(config['email'], config['password'])
            self.logger.info('Connection established to SMTP server : ' + config['smtp_server'])
        except KeyError as e:
            message = 'Missing key in configuration : ' + e.message
            self.logger.error(message)
            raise ManagerError(message)
        except Exception as e:
            message = 'Error encountered : ' + e.message
            self.logger.error(message)
            raise ManagerError(message)
    
    def notify(self, subject, msg):
        """
        Notify the notifiees of an event
        """
        # Excepting all errors and logging it
        try:
            message = \
                'To:{0}\n' + \
                'From:' + self.email + \
                '\nSubject:' + subject + \
                '\n\n' + msg + '\n'
            
            for notifiee in self.notifiees:
                self.smtp.sendmail(self.email, notifiee, message.format(notifiee))
        except Exception as e:
            raise NotificationError('Error Encountered: ' + e.message)
    
    def run(self):
        while True:
            for repo in self.repos:
                self.mail.select(repo.email_folder)
                msgs = self.mail.search(None, 'ALL')
                ids = msgs[1][0].split()
                num_ids = len(ids)

                if repo.num_msgs != num_ids:
                    try:
                        self.logger.info('Received email for repository : ' + repo.folder)
                        result, data = self.mail.fetch(ids[-1], '(RFC822)')

                        assert result == 'OK', 'Wrong Result: ' + result
 
                        branch = self.branch_regex.findall(data[0][1])[0].split('/')[-1].strip('\r')
                        commit = self.commit_regex.findall(data[0][1])[0]
                        prev_commit = repo.commit
                        
                        self.logger.info(branch + ', ' + repo.branch + ' -- ' + commit + ', ' + prev_commit)

                        if branch == repo.branch and commit != prev_commit:
                            self.logger.info('Updating repository : ' + repo.folder)
                            
                            # Executing pull
                            repo.pull()

                            # Verifying pull
                            assert commit == repo.commit, 'Repository ' + repo.folder + ' did not update after pull' 

                            self.logger.info('Repository updated from commit ' + prev_commit + ' to commit ' + commit) 
                            self.notify('Repository ' + repo.folder + ' Updated', 
                                        'Repository ' + repo.folder + ' was updated to commit ' +\
                                        commit + ' for the ' + branch + ' branch')
                        repo.num_msgs = num_ids
                    except AssertionError as e:
                        self.logger.error(e.message)
                        self.notify('PyGitd Encountered Error', e.message)
                    except NotificationError as e:
                        self.logger.error('PyGitd Encountered Error', e.message)
                    except Exception:
                        message = 'Error:\n' + traceback.format_exc()
                        self.logger.error(message)
                        
                        # Notifying notifiees of error
                        self.notify('PyGitd Encountered Error', message)
            time.sleep(self.interval)

