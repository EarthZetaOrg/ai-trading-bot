from sys import version_info
from setuptools import setup

if version_info.major == 3 and version_info.minor < 6 or \
        version_info.major < 3:
    print('Your Python interpreter must be 3.6 or greater!')
    exit(1)

from earthzetaorg import __version__

# Requirements used for submodules
api = ['flask']
plot = ['plotly>=4.0']

develop = [
    'coveralls',
    'flake8',
    'flake8-type-annotations',
    'flake8-tidy-imports',
    'mypy',
    'pytest',
    'pytest-asyncio',
    'pytest-cov',
    'pytest-mock',
    'pytest-random-order',
]

jupyter = [
    'jupyter',
    'nbstripout',
    'ipykernel',
    ]

all_extra = api + plot + develop + jupyter

setup(name='earthzetaorg',
      version=__version__,
      description='Crypto Trading Bot',
      url='https://github.com/earthzetaorg/earthzetaorg',
      author='gcarq and contributors',
      author_email='michael.egger@tsn.at',
      license='GPLv3',
      packages=['earthzetaorg'],
      setup_requires=['pytest-runner', 'numpy'],
      tests_require=['pytest', 'pytest-mock', 'pytest-cov'],
      install_requires=[
          # from requirements-common.txt
          'ccxt>=1.18.1080',
          'SQLAlchemy',
          'python-telegram-bot',
          'arrow',
          'cachetools',
          'requests',
          'urllib3',
          'wrapt',
          'scikit-learn',
          'joblib',
          'jsonschema',
          'TA-Lib',
          'tabulate',
          'coinmarketcap',
          'scikit-optimize',
          'filelock',
          'py_find_1st',
          'python-rapidjson',
          'sdnotify',
          'colorama',
          # from requirements.txt
          'numpy',
          'pandas',
          'scipy',
      ],
      extras_require={
          'api': api,
          'dev': all_extra,
          'plot': plot,
          'all': all_extra,
          'jupyter': jupyter,

      },
      include_package_data=True,
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'earthzetaorg = earthzetaorg.main:main',
          ],
      },
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Office/Business :: Financial :: Investment',
          'Intended Audience :: Science/Research',
      ])
