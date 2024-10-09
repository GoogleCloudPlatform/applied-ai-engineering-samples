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
"""
This module establishes the core 'BaseExtractor' abstract base class, laying the foundation for
specialized data extraction classes.
"""

from abc import ABC, abstractmethod


class BaseExtractor(ABC):
    """Defines the foundational interface and behavior for data extractors.

    This abstract class provides a blueprint for concrete extractor
    implementations, facilitating the extraction and processing of data from
    various sources.

    Args:
        filepath (str): The path to the file from which data will be extracted.
        config_file_parameters (dict[str, str]): A dictionary containing
            configuration settings used to customize the extraction process.

    Attributes:
        filepath (str): Stores the path to the input file.
        config_file_parameters (dict[str, str]): Stores the configuration
            parameters.
    """

    def __init__(self, filepath: str, config_file_parameters: dict[str, str]):
        self.filepath = filepath
        self.config_file_parameters = config_file_parameters

    @abstractmethod
    def process(self, output_dir: str):
        """Defines the core data processing logic to be implemented by subclasses.

        This method serves as a placeholder, mandating that derived extractors
        provide concrete implementations for their specific data handling
        mechanisms.

        Args:
            output_dir (str): The directory where processed data will be saved.
        """
        pass
