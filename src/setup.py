from setuptools import setup

setup(
    name='litalerts',
    version='0.2.0',
    py_modules=['litalerts'],
    install_requires=[
        'Click',
        'requests',
        'rfeed',
        'python-dotenv',
        'lxml',
        'pyyaml',
        'beautifulsoup4',
        'pyzotero',
        'nameparser',
        'discord.py',
        'retry'
    ],
    entry_points={
        'console_scripts': [
            'litalerts = litalerts.cli:cli',
            'lazotero = litalerts.zotero:update_zotero',
            'oa-zotero = litalerts.zotero:oa_zotero',
            'oa-discord = litalerts.discord:oa_discord'
        ],
    },
    
    description='OpenAlex-based literature alerts',
    maintainer='John Kitchin',
    maintainer_email='jkitchin@cmu.edu',
    license='MIT'
)
