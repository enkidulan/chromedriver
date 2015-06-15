import os.path
import sys
import os

__BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')
CHROMEDRV_PATH = os.path.join(__BASE_PATH, 'chromedriver')

# little hack to have chrome driver in sys path
os.environ['PATH'] += ':' + __BASE_PATH
