"""Setup configuration for manifest-versioning package."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="manifest-versioning",
    version="0.1.0",
    author="Raj Alamuri",
    author_email="raj@canopy.security",
    description="Lightweight data versioning for ML pipelines without specialized tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/manifest-versioning",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "aws": ["boto3>=1.26.0"],
        "dev": ["pytest>=7.0", "black>=22.0", "flake8>=4.0"],
    },
    entry_points={
        "console_scripts": [
            "manifest-versioning=manifest_versioning.cli:main",
        ],
    },
)
