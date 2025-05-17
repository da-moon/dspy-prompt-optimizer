#!/usr/bin/env python
"""
Setup script for the DSPy Prompt Optimizer package.
"""

from setuptools import setup, find_packages

setup(
    name="prompt_optimizer",
    version="0.1.0",
    description="A tool to optimize prompts using DSPy framework",
    author="Manus",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "dspy-prompt-optimizer=prompt_optimizer.cli:main",
        ],
    },
    python_requires=">=3.10,<3.13",
    install_requires=[
        "dspy-ai>=2.6.23",
        "click>=8.0.0",
        "anthropic>=0.51.0",
    ],
)
