#!/usr/bin/env python
from setuptools import setup, find_packages

# Read version from source
with open('enhanced_theme_generator.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"\'')
            break

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="enhanced-theme-studio",
    version=version,
    author="Soundchazer2k",
    author_email="soundchazer@gmail.com",
    description="A powerful color palette and theme generator built with PyQt6",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Soundchazer2k/enhanced-theme-studio",
    py_modules=["enhanced_theme_generator"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Designers",
        "Topic :: Artistic Software",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.6",
    install_requires=[
        "PyQt6",
        "numpy",
        "pillow",
    ],
    entry_points={
        "console_scripts": [
            "theme-studio=enhanced_theme_generator:run_studio",
        ],
    },
    package_data={
        '': ['LICENSE', '*.md'],
    },
) 