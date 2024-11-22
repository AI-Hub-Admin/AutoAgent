# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    'requests>=2.17.0',
    'uuid>=1.30'
]

extras = dict()
extras['dev'] = []
extras['test'] = extras['dev'] + []

setup(
    name="AutoAgent",   # Required
    version="0.0.2",    # Required
    description="Autonomous AI Agents Framework with Asynchronous Agent Loop Running Environment",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Xichen Derek Ding",
    author_email="dingo0927@126.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="Autonomous Agents,AutoAgent,AI Agents",
    packages=find_packages(where="src"),  # Required
    install_requires=install_requires,    # Required    
    package_dir={'': 'src'},
    python_requires=">=3.4",
    project_urls={
        "homepage": "http://www.deepnlp.org/blog?category=agent",
        "repository": "https://github.com/AI-Hub-Admin/AutoAgent"
    },
)
