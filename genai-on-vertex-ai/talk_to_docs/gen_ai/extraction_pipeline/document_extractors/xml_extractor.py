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
Provides the XmlExtractor class for extracting textual data from XML (.xml) files and organizing t
he extracted data into separate files for structured document processing.
"""

from io import StringIO
import json
import os
import re
import xml.etree.ElementTree as ET

from gen_ai.extraction_pipeline.document_extractors.base_extractor import BaseExtractor


class XmlExtractor(BaseExtractor):
    """
    Extractor class of textual data from XML (.xml) files and chunks sections into separate files.

    This class inherits from the `BaseExtractor` and provides specialized
    functionality
    for extracting text content from .xml documents.

    Args:
        filepath (str): The path to the .docx file.
        config_file_parameters (dict[str, str]): Configuration settings for the
            extraction process.

    Attributes:
        filepath (str): Stores the path to the input file.
        config_file_parameters (dict[str, str]): Stores the configuration
            parameters.
        xml_extraction (str): Configuration parameter fot the extraction method.
            Defaults to "default".
        xml_chunking (str):  Configuration parameter fot the chunking method.
            Defaults to "default".
    """

    def __init__(self, filepath: str, config_file_parameters: dict[str, str]):
        super().__init__(filepath, config_file_parameters)

        self.xml_extraction = config_file_parameters.get(
            "xml_extraction", "default"
        )
        self.xml_chunking = config_file_parameters.get("xml_chunking", "default")
        self.data = None


    def explore(self, root: ET, text: list[str], metadata: dict[str, dict[str, str]]):
        """
        Recursively explores an XML tree structure, extracting relevant information and appending it to a list.

        Args:
            root: An XML element representing the current node being explored.
            text: A list to which extracted information will be appended.
            metadata: A dictionary containing additional context.
        """
        if root.attrib:
            for key, value in root.attrib.items():
                if key == "id":
                    text.append("")
                    person = metadata["participants"][value]
                    line = f"{person}:"
                elif key == "type" and value.lower() == "q":
                    line = "Question:"
                elif key == "type" and value.lower() == "a":
                    line = "Answer:"
                else:
                    line = f"{key}: {value}"
                if line:
                    text.append(line.strip())
        if root.text and root.text.strip() != "":
            text.append(root.text.strip())
        for element in root:
            self.explore(element, text, metadata)

    def create_filepath(
        self, metadata: dict[str, str], section_name: str, output_dir: str
    ) -> str:
        """Constructs a filepath for saving a document section to disk.

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

        for (section_id, section_name), context in document_chunks.items():
            filepath = self.create_filepath(metadata, section_name, output_dir)

            with open(filepath + ".txt", "w", encoding="utf-8") as f:
                f.write(context)
            temp_metadata = metadata.copy()
            temp_metadata.pop("filename")
            temp_metadata["section_name"] = section_name.lower()
            if section_id:
                temp_metadata["benefit_id"] = section_id.lower()

            with open(filepath + "_metadata.json", "w", encoding="utf-8") as f:
                json.dump(temp_metadata, f)
        return True

    def process(self, output_dir: str) -> bool:
        """
        Main function that controls the processing of a XML file, including extraction, 
        metadata creation, chunking, and file saving.

        This method assumes the file is in a suitable XML format for the chunking
        logic.

        Args:
            output_dir (str): The directory where the processed files should be
                saved.

        Returns:
            bool: True if processing was successful, False otherwise.
        """
        if self.xml_extraction == "custom1":
            extractor = CustomXmlExtractor(self.filepath, self.config_file_parameters)
            return extractor.process(output_dir)

        elif self.xml_extraction == "custom2":
            ingestor = DefaultXmlIngestor(self.filepath)
            self.data = ingestor.extract_document()
            if self.data is None:
                return False
            metadata_creator = CustomXmlMetadataCreator(self.filepath, self.data)
            metadata, transcript_metadata = metadata_creator.create_metadata()
            if not metadata:
                return False
            section_name = metadata["section_name"]
            document_list = [section_name]
            document_list.append(f"Date: {metadata['date']}")
            self.explore(self.data.find("body"), document_list, transcript_metadata)
            document = "\n".join(document_list)
            document_chunks = {(section_name, section_name): document}
            if not self.create_files(document_chunks, metadata, output_dir):
                return False
            return True

        return False

class CustomXmlExtractor(BaseExtractor):
    """
    Extractor class of textual data from XML (.xml) files and chunks sections into separate files.

    This class inherits from the `BaseExtractor` and provides specialized
    functionality
    for extracting text content from .xml documents.

    Args:
        filepath (str): The path to the .docx file.
        config_file_parameters (dict[str, str]): Configuration settings for the
            extraction process.

    Attributes:
        filepath (str): Stores the path to the input file.
        config_file_parameters (dict[str, str]): Stores the configuration
            parameters.
        xml_extraction (str): Configuration parameter fot the extraction method.
            Defaults to "default".
        xml_chunking (str):  Configuration parameter fot the chunking method.
            Defaults to "default".
    """

    def __init__(self, filepath: str, config_file_parameters: dict[str, str]):
        super().__init__(filepath, config_file_parameters)

        self.xml_extraction = config_file_parameters.get(
            "xml_extraction", "default"
        )
        self.xml_chunking = config_file_parameters.get("xml_chunking", "default")
        self.data = None

    def modify_file(self):
        """
        Modifies an existing file by adding a ProcessGroup block and other blocks if 
        they are not already present within the file.
        """
        with open(self.filepath, "r", encoding="utf-8") as file:
            original_lines = file.readlines()

        basename = os.path.basename(self.filepath)
        if basename not in original_lines[0]:
            with open(self.filepath, "w", encoding="utf-8") as file:
                file.write(f'<ProcessGroup Name="{basename}">\n')
                file.write("<ProcessGroupItems>\n")

                for line in original_lines:
                    file.write(line)

                file.write("</ProcessGroupItems>\n")
                file.write("</ProcessGroup>\n")

    def explore_xml_tree(
        self,
        root: ET,
        content: dict[str, tuple[str, str, str]],
        name: list[str],
        visited: set[str],
    ):
        """
        Recursively explores an XML tree, extracting process information and building content for a structured document.

        Args:
            root: The root element of the XML tree.
            content: A dictionary to store extracted content.
            name: A list used to track the hierarchy of process names during
                traversal.
            visited: A set to keep track of visited section IDs and avoid
                duplicates.
        """
        if root.tag == "ProcessGroup":
            name.append(root.attrib["Name"])
        for process_group_items in root.findall("ProcessGroupItems"):
            for item in process_group_items:
                if item.tag == "ProcessGroup":
                    self.explore_xml_tree(item, content, name, visited)
                    name.pop()
                elif item.tag == "Process":
                    section_id = item.attrib["Id"]
                    if section_id in visited:
                        continue
                    visited.add(section_id)
                    name.append(item.attrib["Name"])
                    key = " --- ".join([section_id] + name)
                    group = item.attrib["Group"]
                    page_content = key
                    page_content += f"\n\nName: {item.attrib['Name']}"
                    page_content += f"\nObjective: {item.attrib['Objective']}"
                    page_content += f"\nID: {section_id}"
                    page_content += f"\nGroup: {group}"
                    for line in item.iter():
                        if line.tag == "Text" or line.tag == "Attachment":
                            page_content += "\n" + str(line.text)
                    content[key] = (section_id, group, page_content)
                    name.pop()

    def create_metadata(
        self, key: str, value: tuple[str, str, str], filepath: str
    ):
        """
        Generates and saves a JSON metadata file associated with a processed section of content.

        Args:
            key (str): A string representing the filename, document name and section
                name.
            value (str): A tuple containing (section_id, group,
                formatted_page_content).
            filepath (str): The base filepath where the metadata file will be saved.
        """
        _, filename, *mid = key.split(" --- ")
        section_id, group, _ = value
        metadata = {
            "group_name": "se",
            "file_type": "section",
            "section_number": section_id,
            "group": group,
            "document_name": mid[0] if len(mid) > 0 else "",
            "section_name": " ".join(mid).lower().replace("  ", " "),
            "filename": filename,
            "chunk_number": "0",
        }
        with open(filepath + "_metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f)

    def create_filepath(self, section_name: str, output_dir: str) -> str:
        """
        Creates a file-system-friendly path for saving a document section.

        * Combines higher-level group names.
        * Removes leading digits, whitespace, and hyphens from the section name.
        * Replaces non-alphanumeric characters with underscores.
        * Condenses multiple underscores into single underscores.

        Args:
            section_name (str): The name of the section being saved.
            output_dir (str): The directory where the generated file should be
                saved.

        Returns:
            str: A filepath constructed from the provided information.
        """
        filename = re.sub(r"^\d+\s*-+", "", section_name.lower())
        filename = re.sub(r"[^\w\s&0-9]|(\s+)", "_", filename)
        filename = re.sub(r"_+", "_", filename)
        filename = re.sub(r"(_$)", "", filename)
        filename = "se" + filename
        filepath = os.path.join(output_dir, filename)
        return filepath

    def create_file(
        self, content: dict[str, tuple[str, str, str]], output_dir: str
    ):
        """
        Creates text files and associated metadata files from a content dictionary.

        Args:
            content: A dictionary where keys are hierarchical structures and values
                are tuples containing (section_id, group, formatted_page_content).
            output_dir: The directory where the output files will be saved.
        """
        visited = set()
        for key, value in content.items():
            filepath = self.create_filepath(key, output_dir)

            if filepath in visited:
                continue
            visited.add(filepath)
            page_content = value[2]
            with open(filepath + ".txt", "w", encoding="utf-8") as f:
                f.write(page_content)

            self.create_metadata(key, value, filepath)

    def process(self, output_dir: str) -> bool:
        """
        Main function that controls the processing of a XML file, including extraction, 
        metadata creation, chunking, and file saving.

        This method assumes the file is in a suitable XML format for the chunking logic.

        Args:
            output_dir (str): The directory where the processed files should be
                saved.

        Returns:
            bool: True if processing was successful, False otherwise.
        """
        self.modify_file()

        tree = ET.parse(self.filepath)
        root = tree.getroot()
        content = {}

        self.explore_xml_tree(root, content, [], set())
        if not content:
            return False
        self.create_file(content, output_dir)
        return True

class DefaultXmlIngestor:
    """
    Default ingestor class that provides methods for extracting content from xml files.

    Args:
        filepath (str): The path to the json file.

    Attributes:
        filepath (str): The path to the json file.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

    def extract_document(self) -> ET.Element | None:
        """
        Extracts an XML document from a file.

        This method attempts to read an XML file from the specified `filepath` and parse it into an `ET.Element` 
        object using `ET.iterparse`. It also cleans up the element tags by removing any namespaces.

        Returns:
            ET.Element | None: The root element of the parsed XML document, or `None` if an error occurs during file 
            opening or parsing.
        """
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                xml = f.read()
            it = ET.iterparse(StringIO(xml))
            for _, el in it:
                _, _, el.tag = el.tag.rpartition("}")
            return it.root
        except OSError as e:
            print(f"Error: Unable to open or process the file '{self.filepath}' due to an OS error: {e}")
            return None
        except ET.ParseError as e:
            print(f"Error: Invalid XML format in '{self.filepath}': {e}")
            return None

class CustomXmlMetadataCreator():
    """
    Custom personalized class for creating metadata from xml files.

    Provides a basic metadata structure including the filename.
    """

    def __init__(self, filepath: str, data: ET.Element):
        self.filepath = filepath
        self.data = data

    def parse_transcript_meta(self):
        """
        Parses specific metadata from the XML transcript.

        Returns:
            A dictionary containing extracted metadata:
                - title (str): The title of the transcript.
                - date (str): The date of the transcript.
                - companies (list[str]): A list of companies mentioned in the transcript.
                - participants (dict[str, str]): A dictionary of participant IDs and their 
                  information (title, affiliation, name).
        """
        metadata = {}
        root = self.data.find("meta")
        for element in root:
            if element.tag == "title":
                metadata["title"] = element.text
            elif element.tag == "date":
                metadata["date"] = element.text
            elif element.tag == "companies":
                companies = []
                for company in element:
                    companies.append(company.text)
                metadata["companies"] = companies
            elif element.tag == "participants":
                participants = {}
                for participant in element:
                    participant_id = participant.attrib["id"]
                    title = participant.attrib.get("title")
                    affiliation = participant.attrib.get("affiliation")
                    name = participant.text
                    participant_info = ""
                    if title:
                        participant_info += f"{title}"
                    if affiliation:
                        participant_info += f", {affiliation}"
                    participant_info += f"\n{name}"
                    participants[participant_id] = participant_info
                metadata["participants"] = participants
        return metadata

    def create_metadata(self) -> tuple[dict[str, str], dict[str, str]]:
        """
        Creates a combined metadata dictionary.

        Returns:
            A tuple containing two dictionaries:
                - The first dictionary contains basic file information and some parsed transcript metadata.
                - The second dictionary contains the full parsed transcript metadata.
        """
        metadata = {
            "data_source": "transcipt",
            "symbols": "",
            "filing_type": "",
            "period": "",
            "section_name": "",
            "date": "",
            "original_filepath": "",
            "filename": "",
        }

        metadata["original_filepath"] = os.path.basename(self.filepath)
        filename = os.path.basename(self.filepath)
        filename = os.path.splitext(filename)[0]
        metadata["filename"] = filename
        transcript_metadata = self.parse_transcript_meta()
        metadata["section_name"] = transcript_metadata["title"]
        metadata["date"] = transcript_metadata["date"]
        return metadata, transcript_metadata
