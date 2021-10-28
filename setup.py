from setuptools import setup


setup(
    name='smoof',
    packages=['smoof'],
    version='1.0',
    description = "a tool to quickly explore datasets",
    url = "https://github.com/leopoldavezac/Smoof",
    author = "Leopold Davezac",
    author_email = "leopoldavezac@gmail.com",
    license = "MIT",
    keywords = "dash visualization exploration interactive",
    python_requires = ">=3",
    entry_points={
    'console_scripts': [
        'smoof=smoof.app:main',
        ]
    }

)
