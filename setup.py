from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="wikidata-mcp",
    version="0.2.0",
    author="Led Mishkin",
    author_email="e.baena@northeastern.edu",
    description="Wikidata MCP Server with Vector DB Integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ebaenamar/wikidata-mcp-mirror",
    packages=find_packages(),
    install_requires=requirements,
    package_dir={'': '.'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'wikidata-mcp=wikidata_mcp.api:main',
        ],
    },
    include_package_data=True,
)
