from setuptools import setup, find_packages


# Define the package dependencies. 
# You'll need to manually list the dependencies from your `pyproject.toml` here.
# Install Poetry and run `poetry export -f requirements.txt --output requirements.txt`
# To auto-generate the dependencies
install_requires = [] 
with open("requirements.txt", "r", encoding="utf-8") as f:
    install_requires = f.read().splitlines()

setup(
    name="talktodata",        # This should match the project name in pyproject.toml
    version="0.1.0",        # Initial version; can be dynamically fetched later
    authors = ["msubasioglu","l-sri","orpzs"],    
    description="Open Data QnA",
    long_description="Open Data QnA - Chat with your SQL Database",
    url="https://github.com/GoogleCloudPlatform/applied-ai-engineering-samples@opendataqna",
    project_urls={
        "Bug Tracker": "https://github.com/GoogleCloudPlatform/applied-ai-engineering-samples@opendataqna/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},  # To include the root-level modules
    packages=find_packages(where="."),  # Assuming your modules are in subdirectories
    install_requires=install_requires,
    python_requires=">=3.8",          # Specify your minimum Python version
)
