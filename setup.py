#!/usr/bin/env python3
"""
COSMOS-HGP Setup Script
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cosmos-hgp",
    version="1.0.0",
    author="COSMOS-HGP Team",
    author_email="team@cosmos-hgp.com",
    description="COSMOS-HGP (Cosmic Hierarchical Genetic Processing) - 차세대 AI 시스템 통합 플랫폼",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/COSMOS-HGP",
    packages=find_packages(exclude=["pro", "core_modules", "tests"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "web": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.5.0",
            "numpy>=1.24.0",
            "pandas>=2.0.0",
            "python-multipart>=0.0.6",
        ],
    },
    entry_points={
        "console_scripts": [
            "cosmos-hgp=cosmos.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "cosmos": ["*.py", "*.md"],
        "web": ["*.html", "*.js", "*.css", "*.json"],
    },
    keywords="ai, machine-learning, genetic-algorithm, hierarchical-processing, cosmos, hgp",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/COSMOS-HGP/issues",
        "Source": "https://github.com/yourusername/COSMOS-HGP",
        "Documentation": "https://github.com/yourusername/COSMOS-HGP/wiki",
    },
)