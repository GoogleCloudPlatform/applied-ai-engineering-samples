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
Provides the HtmlExtractor class for extracting textual data from HTML files and organizing the
extracted data into separate files for structured document processing.
"""

import json
import os
import re
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from gen_ai.extraction_pipeline.document_extractors.base_extractor import BaseExtractor
import markdownify


class HtmlExtractor(BaseExtractor):
    """Extractor class of textual data from HTML files and chunks sections into separate files.

    This class inherits from the `BaseExtractor` and provides specialized
    functionality for extracting text content from HTML documents.

    Args:
        filepath (str): The path to the .docx file.
        config_file_parameters (dict[str, str]): Configuration settings for the
          extraction process.

    Attributes:
        filepath (str): Stores the path to the input file.
        config_file_parameters (dict[str, str]): Stores the configuration
          parameters.
        html_extraction (str): Configuration parameter fot the extraction
          method. Defaults to "default".
        html_chunking (str):  Configuration parameter fot the chunking method.
          Defaults to "default".
    """

    def __init__(self, filepath: str, config_file_parameters: dict[str, str]):
        super().__init__(filepath, config_file_parameters)
        self.html_extraction = config_file_parameters.get(
            "html_extraction", "default"
        )
        self.html_chunking = config_file_parameters.get(
            "html_chunking", "default"
        )
        self.data = None

    def create_filepath(
        self, metadata: dict[str, str], section_name: str, output_dir: str
    ) -> str:
        """Creates a file-system-friendly path for saving a document section.

        * Removes extension of the filename
        * Removes leading digits, whitespace, and hyphens from the section name.
        * Condenses multiple underscores into single underscores.

        Args:
            metadata (dict[str, str]): A dictionary containing document
              metadata, including a "filename" key.
            section_name (str): The name of the section being saved.
            output_dir (str): The directory where the generated file should be
              saved.

        Returns:
            str: A filepath constructed from the provided information.
        """

        filename = os.path.splitext(metadata["filename"])[0]
        filename += f"-{section_name.lower()}"
        filename = re.sub(r"[^\w.-]", "_", filename)
        filename = re.sub(r"__+", "_", filename).rstrip("_")
        filepath = os.path.join(output_dir, filename)
        return filepath

    def create_files(
        self,
        document_chunks: dict[tuple[str, str], str],
        metadata: dict[str, str],
        output_dir: str,
    ) -> bool:
        """Saves document sections and associated metadata to individual files.

        The function iterates over a dictionary of document chunks, generates
        filepaths, and writes both the text content and a corresponding metadata
        JSON file output directory.

        Args:
            document_chunks (dict[tuple[str, str], str]): A dictionary where
              keys are tuples of (section_id, section_title) and values are the
              corresponding text content.
            metadata (dict[str, str]):  Metadata associated with the overall
              document.
            output_dir (str):  The target directory for saving the output files.

        Returns:
            bool: True to indicate successful file creation.
        """
        for (_, section_name), context in document_chunks.items():
            filepath = self.create_filepath(metadata, section_name, output_dir)

            with open(filepath + ".txt", "w", encoding="utf-8") as f:
                f.write(context)
            temp_metadata = metadata.copy()
            temp_metadata.pop("filename")
            with open(filepath + "_metadata.json", "w", encoding="utf-8") as f:
                json.dump(temp_metadata, f)
        return True

    def process(self, output_dir: str) -> bool:
        if self.html_extraction == "custom":
            ingestor = CustomHtmlIngestor(self.filepath)
        else:
            ingestor = DefaultHtmlIngestor(self.filepath)
        self.data = ingestor.extract_document()

        patterns = {
            CustomMetadataCreatorOne:r"(\d{10}-\d{2}-\d{6})",
            CustomMetadataCreatorTwo:r"sa_story_\d{7}",
        }
        metadata_creator = None
        for mcreator, pattern in patterns.items():
            fname = os.path.basename(self.filepath)
            if re.match(pattern, fname):
                metadata_creator = mcreator(self.filepath)
        metadata_creator = metadata_creator or DefaultMetadataCreator(self.filepath)
        metadata = metadata_creator.create_metadata()
        if not metadata:
            return False

        filename = metadata.get("filename")
        document_chunks = {(self.filepath, filename): self.data}
        if not self.create_files(document_chunks, metadata, output_dir):
            return False
        return True


class DefaultHtmlIngestor:
    """Default extractor class that provides methods for extracting content from html files.

    Args:
        filepath (str): The path to the html file.

    Attributes:
        filepath (str): The path to the html file.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

    @staticmethod
    def extract_text_from_html(html_text: str) -> str | None:
        """Extracts and cleans up text from an HTML tags.

        Args:
            html_text: The HTML string to process.

        Returns:
            str: The extracted and cleaned text.
        """
        tags = (
            "<br>",
            "<p>",
            "<li>",
            "<ul>",
            "</li>",
            "<hr>",
            "<div>",
            "</ul>",
            "<td>",
            "<tr>",
            "<h1>",
            "<h2>",
            "<h3>",
            "<h4>",
            "<h5>",
            "<h6>",
        )
        text = re.sub(
            r"<[^>]+>",
            lambda match: ("\n" if match.group(0) in tags else " "),
            html_text,
        )
        text = re.sub(r"&nbsp;", " ", text)

        while True:
            new_text = re.sub(r"\n{3}", "\n\n", text)
            new_text = re.sub(r"^\s+", "", new_text)
            if new_text == text:
                break
            text = new_text
        if new_text:
            return new_text
        return None

    @staticmethod
    def extract_from_html_using_markdownify(html_text: str) -> str | None:
        """Converts an HTML string to Markdown format.

        Args:
            html_text (str): The HTML string to convert.

        Returns:
            str: The converted Markdown text.
        """
        try:
            markdown_text = markdownify.markdownify(html_text)
            return markdown_text
        except TypeError as e:
            print(f"An error occurred during conversion: {e}")
            return None

    def extract_document(self) -> str:
        """
        Extracts text from a file specified by the "filepath" attribute and 
        converts it into Markdown format.

        Args:
            None

        Returns:
            str: The extracted text in Markdown format.

        Raises:
            IOError: If an error occurs while opening or reading the file.
            UnicodeDecodeError: If the file's encoding is not UTF-8.
        """
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = f.read()
            markdowned_text = DefaultHtmlIngestor.extract_from_html_using_markdownify(str(data))
            return markdowned_text

        except IOError as e:
            print(f"Error: An error occurred while reading the file: {e}")
            raise IOError(f"Error: An error occurred while reading the file: {e}") from e

        except UnicodeDecodeError as e:
            print(f"Error: File is not in UTF-8 encoding: {e}")
            raise UnicodeDecodeError(f"Error: File is not in UTF-8 encoding : {e}") from e


class CustomHtmlIngestor:
    """Custom Extractor class processes HTML files, specifically handling ordered lists, tables and other HTML tags.

    It offers methods to extract content from HTML and convert it cleanly into
    Markdown formatting.

    Args:
        filepath (str): The path to the html file.

    Attributes:
        filepath (str): The path to the html file.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

    def extract_document(self) -> str:
        """Processes a Custom HTML file and returns its contents in Markdown format.

        Parses the HTML file, removes hidden divs and empty tables, and then 
        converts the remaining HTML structure into Markdown using the "markdownify" library.

        Args:
            None

        Returns:
            str: The extracted document content represented as a Markdown string.

        Raises:
            IOError: If an error occurs while reading the file.
            UnicodeDecodeError: If the file is not in UTF-8 encoding.
        """
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = BeautifulSoup(f, "html.parser")
            for div in data.find_all("div", style="display:none"):
                div.decompose()
            for table in data.find_all("table"):
                all_cells_empty = all(cell.get_text(strip=True) == "" for cell in table.find_all(["td", "th"]))
                if all_cells_empty:
                    table.decompose()
            for script_tag in data.find_all("script"):
                script_tag.decompose()

            for link in data.find_all("a"):
                text_content = link.text
                if "table of contents" in text_content.lower():
                    link.decompose()

            markdowned_text = markdownify.markdownify(str(data), strip=["a"])
            markdowned_text = re.sub(r"[\u00A0\u2007\u202F]", "", markdowned_text)
            return markdowned_text

        except IOError as e:
            print(f"Error: An error occurred while reading the file: {e}")
            raise IOError(f"Error: An error occurred while reading the file: {e}") from e

        except UnicodeDecodeError as e:
            print(f"Error: File is not in UTF-8 encoding: {e}")
            raise UnicodeDecodeError(f"Error: File is not in UTF-8 encoding : {e}") from e


class DefaultMetadataCreator:
    """Default class for creating metadata.

    Provides a basic metadata structure including the filename.

    Args:
        filepath (str): The path to the file.

    Attributes:
        filename (str): The name of the file (without the path).
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

    def create_metadata(self) -> dict[str, str]:
        """A method to be implemented by subclasses.

        Generates a dictionary of metadata extracted from the file.

        Returns:
            dict[str, str]: A dictionary containing metadata keys and their
            corresponding values.
        """
        metadata = {
                "original_filepath": "",
                "filename": "",
            }
        metadata["original_filepath"] = os.path.basename(self.filepath)
        filename = os.path.basename(self.filepath)
        filename = os.path.splitext(filename)[0]
        metadata["filename"] = filename
        return metadata


class CustomMetadataCreatorOne(DefaultMetadataCreator):
    """Custom class for creating metadata for 10K.

    Provides a basic metadata structure including the filename.

    Args:
        filepath (str): The path to the file.

    Attributes:
        filename (str): The name of the file (without the path).
    """
    def parse_edgar_data(self, file_path):
        """Parses sgml data from the specified file.

        Args:
            file_path (str): The path to the EDGAR data file.

        Returns:
            dict[str,dict[str,str]]: A list of dictionaries, where each dictionary represents
                        a parsed record.
        """

        records = {}
        current_record = {}

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() == "<<>>":
                    if current_record:
                        records[current_record["id"]]=current_record
                    current_record = {}
                else:
                    key, value = line.split("\t", 1)
                    current_record[key] = value.strip()

        if current_record:
            records.append(current_record)

        return records

    def create_metadata(self) -> dict[str, str]:
        """A method to be implemented by subclasses.

        Generates a dictionary of metadata extracted from the html file.

        Returns:
            dict[str, str]: A dictionary containing metadata keys and their
            corresponding values.
        """
        metadata = {
                "data_source":"10k",
                "symbols":"",
                "filing_type":"",
                "period":"",
                "section_name":"",
                "date":"",
                "original_filepath": "",
                "filename": "",
            }
        metadata["original_filepath"] = os.path.basename(self.filepath)
        filename = os.path.basename(self.filepath)
        filename = os.path.splitext(filename)[0]
        metadata["filename"] = filename
        match = re.search(r"(\d{10}-\d{2}-\d{6})", filename)
        if match:
            dir_path = os.path.dirname(self.filepath)
            sgml_filename = match.group(1) + ".sgml-fields"
            sgml_filepath = os.path.join(dir_path, sgml_filename)
            sgml_data = self.parse_edgar_data(sgml_filepath)
            if filename in sgml_data:
                metadata["section_name"] = sgml_data[filename]["headline"]
                metadata["filing_type"] = sgml_data[filename]["filing_type"]
                metadata["symbols"] = sgml_data[filename]["symbols"]
                metadata["period"] = sgml_data[filename]["period"]
        return metadata


class CustomMetadataCreatorTwo(DefaultMetadataCreator):
    """Custom class for creating metadata for SA.

    Provides a basic metadata structure including the filename.

    Args:
        filepath (str): The path to the file.

    Attributes:
        filename (str): The name of the file (without the path).
    """
    def parse_fdsxml_data(self, file_path: str) -> dict[str, str]:
        """Parses fdsxml data from the specified file.

        Args:
            file_path (str): The path to the fdsxml data file.

        Returns:
            dict[str,dict[str,str]]: A list of dictionaries, where each dictionary represents
                        a parsed record.
        """

        records = {}

        def xplore(root, data: dict[str, str]):
            for element in root:
                if element.tag=="field":
                    item = element.attrib["name"]
                    value = element.text
                    data[item] = value
                xplore(element, data)

        tree = ET.parse(file_path)
        root = tree.getroot()
        xplore(root, records)
        return records

    def create_metadata(self) -> dict[str, str]:
        """A method to be implemented by subclasses.

        Generates a dictionary of metadata extracted from the html file.

        Returns:
            dict[str, str]: A dictionary containing metadata keys and their
            corresponding values.
        """
        metadata = {
                "data_source":"sa",
                "symbols":"",
                "filing_type":"",
                "period":"",
                "section_name":"",
                "date":"",
                "original_filepath": "",
                "filename": "",
            }
        metadata["original_filepath"] = os.path.basename(self.filepath)
        filename = os.path.basename(self.filepath)
        filename = os.path.splitext(filename)[0]
        metadata["filename"] = filename
        match = re.search(r"(sa_story_\d{7})", filename)
        if match:
            dir_path = os.path.dirname(self.filepath)
            fdsxml_filename = match.group(1) + ".fdsxml"
            fdsxml_filepath = os.path.join(dir_path, fdsxml_filename)
            fdsxml_data = self.parse_fdsxml_data(fdsxml_filepath)
            metadata["section_name"] = fdsxml_data["headline"]
            metadata["symbols"] = fdsxml_data["symbols"]
            metadata["date"] = fdsxml_data["story_date"]
        return metadata
