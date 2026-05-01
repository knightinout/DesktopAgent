#!/usr/bin/env python3
"""Setup script for Desktop Agent - AI-powered Linux desktop assistant"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(readme_path, 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(req_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="desktop-agent",
    version="1.0.0",
    author="Desktop Agent Contributors",
    author_email="noreply@github.com",
    description="AI-powered Linux desktop assistant for file organization and system automation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/knightinout/DesktopAgent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Desktop Environment :: File Managers",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "desktop-agent=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    keywords="ai assistant desktop linux automation file-organizer xfce ubuntu",
    project_urls={
        "Bug Reports": "https://github.com/knightinout/DesktopAgent/issues",
        "Source": "https://github.com/knightinout/DesktopAgent",
        "Documentation": "https://github.com/knightinout/DesktopAgent#readme",
    },
)