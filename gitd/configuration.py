"""Configuration for the Git Daemon
"""
import yaml

from repo import Repo
from exc import ConfigurationError

class Configuration:
    """Configuration Object
    """

    def __init__(self, config_file):
        """Constructor

        Args:
            config_file (:obj:`str`): YAML configuration file
        """
        config = None

        with open(config_file, 'r'):
            config = yaml.safe_load(config_file)

        self.repos = [Repo(**config) for config in config['repos']]

        try:
            # General Information
            self.notifiees = config['notification_recipients']
            self.interval = config['interval']
            self.email = config['email']

            # IMAP Connection
            self.imap_server = config['imap_server']
            self.email = config['email']
            self.password = config['password']

            # SMTP Connection
            self.smtp_server = config['smtp_server']
            self.smtp_port = config['smtp_port']
        except KeyError as e:
            raise ConfigurationError("Missing configuration key: {}".format(e.message))
