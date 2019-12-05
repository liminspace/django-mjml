import os
import sys


sys.path.insert(0,  os.path.abspath(os.path.dirname((__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testprj.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
