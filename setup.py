from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="awesome-ai-learning",
    version="0.1.0",
    author="Nick Westburg",
    author_email="",
    description="Automated GitHub stars organization and AI learning resource curation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/W3STY11/awesome-ai-learning",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyGithub>=2.1.1",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
        "nltk>=3.8.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "tqdm>=4.65.0",
        "click>=8.1.0",
    ],
    entry_points={
        "console_scripts": [
            "fetch-stars=tools.fetch_stars:main",
            "analyze-repos=tools.analyze_repos:main",
            "generate-pages=tools.generate_markdown:main",
        ],
    },
)