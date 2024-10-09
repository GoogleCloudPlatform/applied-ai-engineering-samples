# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from setuptools import setup, find_packages
from pkg_resources import parse_requirements
import os


def get_requirements(filename):
    with open(filename) as f:
        requirements = [str(req) for req in parse_requirements(f)]
    return requirements


version = "0.1.1"

with open(os.path.join("gen_ai", "version.txt"), "w") as version_file:
    version_file.write(version)

setup(
    name="gen_ai",
    version=version,
    packages=find_packages(include=["gen_ai"]),
    install_requires=get_requirements("requirements.txt"),
    author="Google LLC",
    author_email="chertushkin@google.com",
    description="This is pipeline code for accelerating solution accelerators",
    long_description=open("README.md").read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
)
