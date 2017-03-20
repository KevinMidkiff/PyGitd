# import json
# from PyGitd.manager import Manager

# with open('/home/pi/PyGitd/example_config.json', 'r') as f:
#     config = json.load(f)

# m = Manager(config)
# m.run()
from gitd import Configuration

c = Configuration('config.yaml')
