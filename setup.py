from setuptools import setup, find_packages

requires = [
    'tornado',
    'tornado-sqlalchemy'
]

setup(
    name='letsfuk',
    version='0.0',
    description='Group anonymous chat',
    author='Strahinja Kovacevic',
    author_email='strahinja.kovacevic994@gmail.com',
    keywords='chat anonymous',
    packages=find_packages(),
    install_requires=requires,
)
