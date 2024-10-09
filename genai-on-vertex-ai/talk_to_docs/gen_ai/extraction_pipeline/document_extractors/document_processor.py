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
"""Module for flexible document processing based on file extensions.

This module defines the `DocumentProcessor` class, which intelligently selects
and uses extractor classes from the `EXTRACTORS_MAP` to handle documents of
various supported file types. The extraction configuration can be controlled
through the `config_file_parameters` dictionary.
"""

import os

from gen_ai.extraction_pipeline.document_extractors.docx_extractor import DocxExtractor
from gen_ai.extraction_pipeline.document_extractors.json_extractor import JsonExtractor
from gen_ai.extraction_pipeline.document_extractors.pdf_extractor import PdfExtractor
from gen_ai.extraction_pipeline.document_extractors.xml_extractor import XmlExtractor
from gen_ai.extraction_pipeline.document_extractors.html_extractor import HtmlExtractor

EXTRACTORS_MAP = {
    ".docx": DocxExtractor,
    ".xml": XmlExtractor,
    ".json": JsonExtractor,
    ".pdf": PdfExtractor,
    ".html": HtmlExtractor,
    ".att_ni_xml": XmlExtractor
}


class DocumentProcessor:
    """Handles the processing of documents based on their file extensions.

    This class coordinates the selection of appropriate extractor classes and
    manages the extraction process for supported file types.

    Args:
        filepath (str): The path to the file from which data will be extracted.
        config_file_parameters (dict[str, str]): A dictionary containing
            configuration settings used to customize the extraction process.

    Attributes:
        extractor (Document Extractor Class): An instance of an appropriate
            extractor class, determined by the file extension, or None if
            unsupported.
    """

    def __init__(self, filepath: str, config_file_parameters: dict[str, str]):
        self.extractor = None
        extension = os.path.splitext(filepath)[1]

        if extension in EXTRACTORS_MAP:
            self.extractor = EXTRACTORS_MAP[extension](
                filepath, config_file_parameters
            )
        else:
            print(f"Bypassing {filepath}. Unsupported file type")
            # raise TypeError("Wrong file format")

    def __call__(self, output_dir: str) -> bool:
        """Initiates the document processing workflow.

        Delegates the extraction process to the assigned extractor instance if it
        exists. Handles potential TypeErrors during processing.

        Args:
            output_dir (str): The directory where the extracted data will be saved.

        Returns:
            bool: True if the processing was successful, False otherwise.
        """
        if not self.extractor:
            return False
        try:
            if not self.extractor.process(output_dir):
                return False
        except Exception as e: # pylint: disable=W0718
            print(e)
            return False
        return True
