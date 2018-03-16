from setuptools import setup

setup(
    name='gamehivechallengr',
    packages=['gamehivechallengr'],
    include_package_data=True,
    install_requires=[
        'flask',
        'Flask-SQLAlchemy',
        'psycopg2-binary'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)