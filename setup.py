
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Sendero Middleware',
    'author': 'dernster, alarrosa14, kitab15',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'My email.',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['sendero_middleware'],
    'scripts': [],
    'name': 'Sendero'
}

setup(**config)
