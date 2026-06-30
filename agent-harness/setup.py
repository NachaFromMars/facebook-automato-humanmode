from setuptools import setup, find_namespace_packages

setup(
    name='cli-anything-facebook-automato',
    version='0.1.0',
    description='Agent-native CLI harness for Facebook HumanMode/CDP read-only workflows',
    packages=find_namespace_packages(include=['cli_anything.*']),
    install_requires=['click>=8.0', 'websocket-client>=1.6'],
    entry_points={
        'console_scripts': [
            'cli-anything-facebook-automato=cli_anything.facebook_automato.facebook_automato_cli:cli',
            'fbcli=cli_anything.facebook_automato.facebook_automato_cli:cli',
        ],
    },
    python_requires='>=3.9',
)
