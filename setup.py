from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith('#')]

setup(
    name="wikidata-mcp",
    version="0.2.0",
    author="Eduardo Baena",
    author_email="ebaena@example.com",
    description="Wikidata MCP Server with Vector DB Integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ebaenamar/wikidata-mcp-mirror",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=requirements,
    package_data={
        'wikidata_mcp': ['*.py', '**/*.py', '*.json'],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'wikidata-mcp=wikidata_mcp.api:app',
            'wikidata-mcp-serve=wikidata_mcp.__main__:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
