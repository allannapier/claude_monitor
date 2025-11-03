"""Setup file for claude-monitor."""

from setuptools import setup, find_packages

setup(
    name="claude-monitor",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "claude-monitor=claude_monitor.cli:main",
        ],
    },
)
