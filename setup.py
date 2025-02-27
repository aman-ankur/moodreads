from setuptools import setup, find_packages
from pathlib import Path

# Read requirements
def read_requirements(filename: str) -> list:
    try:
        return [
            line.strip() 
            for line in Path(filename).read_text().splitlines() 
            if line.strip() and not line.startswith('#')
        ]
    except FileNotFoundError:
        return []

# Read long description
try:
    long_description = Path('README.md').read_text()
except FileNotFoundError:
    long_description = "Moodreads - An emotional book recommendation system"

setup(
    name="moodreads",
    version="0.1.0",
    description="An emotional book recommendation system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/moodreads",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'dev': read_requirements('requirements-dev.txt'),
    },
    entry_points={
        'console_scripts': [
            'moodreads=main:main',
            'moodreads-scraper=scripts.scrape_books:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    include_package_data=True,
    package_data={
        'moodreads': [
            'static/*',
            'templates/*',
        ],
    },
    data_files=[
        ('config', ['config/logging.conf']),
    ],
) 