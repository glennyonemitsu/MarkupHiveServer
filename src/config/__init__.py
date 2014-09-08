import os

if os.environ.get('MARKUPHIVE_DEPLOYMENT', 'development') == 'development':
    from config import development as config
else:
    from config import production as config
