from setuptools import setup

setup(
    name='litalerts',
    version='0.1.0',
    py_modules=['litalerts'],
    install_requires=[
        'Click',
        'requests',
        'rfeed',
        'python-dotenv',
        'lxml',
        'pyyaml',
        'beautifulsoup4'
    ],
    entry_points={
        'console_scripts': [
            'litalerts = litalerts.cli:cli',
        ],
    },
    
    description='OpenAlex-based literature alerts',
    maintainer='John Kitchin',
    maintainer_email='jkitchin@cmu.edu',
    license='MIT'
)
