# gesture_ui/wsgi.py

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gesture_ui.settings')

application = get_wsgi_application()