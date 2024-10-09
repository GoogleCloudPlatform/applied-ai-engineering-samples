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
"""Provides the JsonExtractor class for extracting textual data from json files.

And organizing the extracted data into separate files for structured document
processing.
"""
import copy
import datetime
import json
import os
import re
from typing import Any

from gen_ai.extraction_pipeline.document_extractors.base_extractor import BaseExtractor
from gen_ai.extraction_pipeline.document_extractors.docx_extractor import DefaultDocxExtractor, DefaultDocxChunker, CustomKcDocxChunker
from gen_ai.extraction_pipeline.document_extractors.html_extractor import DefaultHtmlIngestor
from gen_ai.extraction_pipeline.document_extractors.pdf_extractor import DefaultPdfExtractor


class DefaultJsonExtractor:
    """Default extractor class that provides methods for extracting content from json files.

    Args:
        filepath (str): The path to the json file.

    Attributes:
        filepath (str): The path to the json file.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

    def extract_document(self) -> dict[str, Any]:
        """Extracts data from the json file.

        Returns:
            dict: The deserialized JSON data as a Python dictionary.
        """
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error decoding JSON data: {e}", doc=self.filepath, pos=0)


class DefaultJsonMetadataCreator:
    """Default class for creating metadata from json files.

    Provides a basic metadata structure including the filename.

    Args:
        filepath (str): The absolute path to the JSON file.
        data (dict[str, Any]): The parsed JSON data represented as a dictionary.

    Attributes:
        filepath (str): The absolute path to the JSON file.
        data (dict[str, Any]): The parsed JSON data represented as a dictionary.
    """

    def __init__(self, filepath: str, data: dict[str, Any]):
        self.filepath = filepath
        self.data = data

    def create_metadata(self) -> dict[str, str]:
        """Abstract method to be implemented by subclasses.

        Generates a dictionary of metadata extracted from the json file.

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


class CustomJsonMetadataCreatorOne(DefaultJsonMetadataCreator):
    """Metadata creator from json class customly created for Custom KC use case.

    Provides a basic metadata structure including the filename, policy name,
    title, etc.

    Args:
        filepath (str): The absolute path to the JSON file.
        data (dict[str, Any]): The parsed JSON data represented as a dictionary.

    Attributes:
        filepath (str): The absolute path to the JSON file.
        data (dict[str, Any]): "metadata" field of the parsed JSON data
          represented as a dictionary.
    """

    def __init__(self, filepath: str, data: dict[str, Any]):
        super().__init__(filepath, data)
        # self.filepath = filepath
        self.data = data.get("metadata")
        if not self.data:
            raise TypeError("Wrong type of KC json data")

    def create_metadata(self) -> dict[str, str]:
        """Generates a metadata dictionary from a KC JSON file.

        Checks for a valid content type ("text/html") and extracts relevant
        metadata
        fields from the JSON data. Handles potential "None" values within the
        data.

        Args:
            self: The instance of the class.

        Returns:
            dict[str, str]: A dictionary containing KC-specific metadata keys
            and their corresponding values.

        Raises:
            TypeError: If the JSON data does not have the expected "text/html"
            mimeType.
        """
        metadata = {
            "data_source": "kc",
            "policy_number": "",
            "set_number": "",
            "effective_date": "",
            "cancellation_date": "",
            "original_filepath": "",
            "section_name": "",
            "plan_name": "",
            "policy_title": "",
            "url": "",
            "doc_identifier": "",
            "category_name": "",
            "benefit_id": "",
            "filename": "",
        }
        # Sometimes values are None, so need this assignment first
        doc_identifier = self.data["structData"].get("doc_identifier")
        section_name = self.data["structData"].get("name")
        url = self.data["structData"].get("url")
        policy_number = self.data["structData"].get("policy_number")

        metadata["doc_identifier"] = (
            doc_identifier.lower().strip() if doc_identifier else ""
        )
        metadata["section_name"] = (
            section_name.lower().strip() if section_name else ""
        )
        metadata["url"] = url if url else ""
        metadata["policy_number"] = policy_number if policy_number else "generic"
        metadata["original_filepath"] = os.path.basename(self.filepath)

        filename = os.path.basename(self.filepath)
        filename = os.path.splitext(filename)[0]
        metadata["filename"] = filename
        return metadata


class CustomJsonMetadataCreatorTwo(DefaultJsonMetadataCreator):
    """Metadata creator from json class customly created for Custom B360 use case.

    Provides a basic metadata structure including the filename, policy name,
    title, etc.

    Args:
        filepath (str): The absolute path to the JSON file.
        data (dict[str, Any]): The parsed JSON data represented as a dictionary.

    Attributes:
        filepath (str): The absolute path to the JSON file.
        data (dict[str, Any]): "metadata" field of the parsed JSON data
          represented as a dictionary.
    """

    def create_metadata(self) -> dict[str, str]:
        """Method that generates a dictionary of metadata for Custom B360, extracted from the json file.

        Returns:
            dict[str, str]: A dictionary containing metadata keys and their
            corresponding values.
        """
        metadata = {
            "data_source": "b360",
            "policy_number": "",
            "set_number": "",
            "effective_date": "",
            "cancellation_date": "",
            "original_filepath": "",
            "section_name": "",
            "plan_name": "",
            "policy_title": "",
            "url": "",
            "doc_identifier": "",
            "category_name": "",
            "benefit_id": "",
            "filename": "",
        }
        category_name = self.data.get("categoryName")
        policy_number = self.data.get("policyNumber")
        set_number = self.data.get("setId")
        filename = f"{policy_number}-{set_number}-{category_name}"
        filename = re.sub(r"[^\w.-]", "_", filename)
        filename = re.sub(r"__+", "_", filename).rstrip("_")

        metadata["category_name"] = (
            category_name.lower().strip() if category_name else ""
        )
        metadata["policy_number"] = (
            policy_number.lower().strip() if policy_number else ""
        )
        metadata["set_number"] = (
            set_number.lower().strip() if set_number else ""
        )
        metadata["original_filepath"] = os.path.basename(self.filepath)
        metadata["filename"] = filename

        return metadata


class CustomJsonMetadataCreatorThree(DefaultJsonMetadataCreator):
    """Metadata creator from json class customly created for Custom B360 use case.

    Provides a basic metadata structure including the filename, policy name,
    title, etc.

    Args:
        filepath (str): The absolute path to the JSON file.
        data (dict[str, Any]): The parsed JSON data represented as a dictionary.

    Attributes:
        filepath (str): The absolute path to the JSON file.
        data (dict[str, Any]): "metadata" field of the parsed JSON data
          represented as a dictionary.
    """

    def create_metadata(self) -> dict[str, str]:
        """Method that generates a dictionary of metadata for Custom B360, extracted from the json file.

        Returns:
            dict[str, str]: A dictionary containing metadata keys and their
            corresponding values.
        """
        metadata = {
            "data_source": "b360",
            "policy_number": "",
            "set_number": "",
            "effective_date": "",
            "cancellation_date": "",
            "original_filepath": "",
            "section_name": "",
            "plan_name": "",
            "policy_title": "",
            "url": "",
            "doc_identifier": "",
            "category_name": "",
            "benefit_id": "",
            "filename": "",
        }
        benefit_id = self.data["BenefitPlan"].get("BenefitPlanID")
        if benefit_id and len(benefit_id.split("_")) == 2:
            policy_number, set_number = benefit_id.split("_")
        else:
            policy_number = set_number = benefit_id
        effective_date = self.data["BenefitPlan"].get("BenefitPlanEffectiveDate")
        if isinstance(effective_date, int):
            effective_date = datetime.datetime.fromtimestamp(effective_date / 1e3).strftime("%Y-%m-%d")
        else:
            effective_date = datetime.datetime.strptime(effective_date, "%m/%d/%Y").strftime("%Y-%m-%d")

        plan_name = self.data["BenefitPlan"].get("BenefitPlanName")

        filename = f"{policy_number}-{set_number}-{plan_name}"
        filename = re.sub(r"[^\w.-]", "_", filename)
        filename = re.sub(r"__+", "_", filename).rstrip("_")

        metadata["plan_name"] = (
            plan_name.lower().strip() if plan_name else ""
        )
        metadata["policy_number"] = (
            policy_number.lower().strip() if policy_number else ""
        )
        metadata["set_number"] = (
            set_number.lower().strip() if set_number else ""
        )
        metadata["url"] = (
            set_number.lower().strip() if set_number else ""
        )
        metadata["doc_identifier"] = (
            f"{metadata['policy_number']}_{metadata['set_number']}"
        )
        metadata["effective_date"] = (
            effective_date if effective_date else ""
        )
        metadata["original_filepath"] = os.path.basename(self.filepath)
        metadata["filename"] = filename

        return metadata


class DefaultJsonChunker:
    """Reads a JSON file and creates simple chunks based on key-value pairs.

    Attributes:
        filepath (str): The path to the JSON file.
        data (dict[str, Any]): The loaded dictionary representation of the JSON
          data.
        config (dict[str, str]): Configuration settings for the extraction process.
    """

    def __init__(self, filepath: str, data: dict[str, Any], config: dict[str, str] | None = None):
        self.filepath = filepath
        self.data = data
        if not config:
            self.config = {}
        else:
            self.config = config

    def chunk_the_document(self) -> dict[tuple[str, str], str]:
        """Creates chunks from the JSON data.

        Returns:
            dict[tuple[str, str], str]:  A dictionary where keys are tuples
              of the form ("", <original JSON key>) and values are the
              corresponding values from the original JSON data.
        """
        return {("", key): value for key, value in self.data.items()}


class CustomJsonChunkerOne(DefaultJsonChunker):
    """Extracts text content from Custom KC Center JSON data and creates a single chunk.

    Inherits from the DefaultJsonChunker class.
    """

    def chunk_the_document(self) -> dict[tuple[str, str], str]:
        """Extracts and processes text from a Custom KC JSON document.

        Returns:
            dict[tuple[str, str], str]: A dictionary containing a single chunk.
                The key is a tuple ("", <section name>) and the value is the
                processed text (section name prepended to the extracted article
                text).

        Raises:
            TypeError: If the "article" key is not found in the JSON data.
        """

        # Check content type for "article". Need to decide if necessary
        output_data = {("", ""): ""}
        mime_type = self.data["metadata"]["content"].get("mimeType") or self.data["metadata"]["content"].get("mimetype")
        if not mime_type:
            raise TypeError("Wrong type of KC json data")
        if "text/html" in mime_type:
            raw_text = self.data.get("article")
            if not raw_text:
                raise TypeError("Wrong type of KC json data")
            processed_text = DefaultHtmlIngestor.extract_from_html_using_markdownify(raw_text)
            section_name = (
                self.data["metadata"]["structData"].get("name", "").strip()
            )
            processed_text = f"{section_name}\n{processed_text}"
            output_data = {("", section_name): processed_text}
        elif "pdf" in mime_type:
            filepath = f"{self.config.get('raw_files_path', 'raw_files')}/{self.data.get('name')}.pdf"
            extractor = DefaultPdfExtractor(filepath)
            elements = extractor.extract_document(self.config)
            processed_text = " \n".join([el.text for el in elements if el not in ("Footer", "Header")])
            section_name = (
                self.data["metadata"]["structData"].get("name", "").strip()
            )
            processed_text = f"{section_name}\n{processed_text}"
            output_data = {("", section_name): processed_text}
        elif "word" in mime_type:
            filepath = f"{self.config.get('raw_files_path', 'raw_files')}/{self.data.get('name')}.docx"
            extractor = DefaultDocxExtractor(filepath)
            document = extractor.extract_document()
            raw_text = extractor.extract_text()
            document_chunker = DefaultDocxChunker(document, raw_text, self.config.get('docx_chunk_level', 1))
            output_data = document_chunker.chunk_the_document()
            additional_chunks = CustomKcDocxChunker(document, raw_text).chunk_the_document()
            if additional_chunks:
                output_data.update(additional_chunks)

        else:
            raise TypeError("Wrong type of KC json data")
        return output_data


class CustomJsonChunkerTwo(DefaultJsonChunker):
    """Parses Custom B360 JSON data and creates text chunks organized by benefit.

    Inherits from the DefaultJsonChunker class.
    """

    def check_html_tags(self, text: str) -> bool:
        """Detects the presence of HTML tags within a text string.

        Args:
            text (str): The text string to examine.

        Returns:
            bool: True if HTML tags are found, False otherwise.
        """
        return bool(re.search(r"<[^>]*>", text))

    def get_values(self, item: dict[str, Any], key: str) -> str:
        """Retrieves and processes a value from a dictionary.

        Args:
            item (dict): The dictionary containing the key-value pair.
            key (str): The key to retrieve.

        Returns:
            str: The retrieved value. If the value contains HTML tags,
                 it is processed using DefaultHtmlIngestor.extract_from_html_using_markdownify.
        """
        value = item.get(key, "")
        if value and self.check_html_tags(value):
            value = DefaultHtmlIngestor.extract_from_html_using_markdownify(value)
        return value

    def chunk_the_document(self) -> dict[tuple[str, str], str]:
        """Creates text chunks from a Custom B360 JSON document.

        Returns:
            dict[tuple[str, str], str]: A dictionary where keys are tuples of
                (benefit ID, section name), and values are the corresponding
                concatenated text chunks.
        """
        output_data = {}
        category_name = self.data.get("categoryName", "")

        for section in self.data["children"]:
            benefit_id = section.get("benefitId", "")
            if not benefit_id:
                break
            section_name = section.get("categoryName", "")
            current_text = f"{category_name}\n{section_name}\n"

            # All benefits have length 1 or 0 for tested files
            if section["benefit"]:
                for item in section["benefit"]:
                    current_text += (
                        f"{self.get_values(item, 'benefitSectionName')}\n"
                    )
                    current_text += f"{self.get_values(item, 'benefitName')}\n"
                    current_text += (
                        f"{self.get_values(item, 'benefitLanguageDescription')}\n"
                    )
                    current_text += "Network Section:\n"
                    if item["benefitNetworkSection"]:
                        for network_info in item["benefitNetworkSection"]:
                            current_text += (
                                "Type:"
                                f" {self.get_values(network_info, 'networkTypeCode')}\n"
                            )
                            if network_info["networkTypeDescription"]:
                                for type_description in network_info[
                                    "networkTypeDescription"
                                ]:
                                    current_text += f"{type_description}\n"
                            current_text += (
                                "Description:"
                                f" {self.get_values(network_info, 'networkLanguageDescription')}\n"
                            )
                    if item["benefitLimitAndException"]:
                        for limit_info in item["benefitLimitAndException"]:
                            current_text += (
                                f"{self.get_values(limit_info, 'description')}\n"
                            )
                            current_text += (
                                f"{self.get_values(limit_info, 'details')}\n"
                            )
            output_data[(benefit_id, section_name)] = current_text
        return output_data


class CustomJsonChunkerThree(CustomJsonChunkerTwo):
    """Parses Custom B360 JSON data and creates text chunks organized by benefit.

    Inherits from the DefaultJsonChunker class.
    """
    def chunk_the_document(self) -> dict[tuple[str, str], str]:
        """Creates text chunks from a Custom B360 JSON document.

        Returns:
            dict[tuple[str, str], str]: A dictionary where keys are tuples of
                (benefit ID, section name), and values are the corresponding
                concatenated text chunks.
        """
        def extract_from_string(item):
            """Extracts text from an HTML string using the DefaultHtmlIngestor class.
            Args:
                item (str): An HTML string.

            Returns:
                str: The extracted text.
            """
            return DefaultHtmlIngestor.extract_from_html_using_markdownify(item)

        def extract_from_list(item):
            """Recursively extracts text from nested lists and concatenates the results.
            Args:
                item (list): A nested list containing strings, dictionaries, and further lists.

            Returns:
                str: The concatenated text extracted from the nested list structure.
            """
            result = ""
            for value in item:
                if isinstance(value, list):
                    result += f"{extract_from_list(value)}\n"
                elif isinstance(value, dict):
                    result += f"{extract_from_dict(value)}\n"
                elif isinstance(value, str):
                    result += extract_from_string(value)
            return result

        def extract_from_dict(item):
            """Recursively extracts text from nested dictionaries, applying formatting based on keys.

            Args:
                item (dict): A nested dictionary containing strings, dictionaries, and further lists.

            Returns:
                str: The concatenated text extracted from the nested dictionary structure, 
                    with formatting applied based on certain keys.
            """
            result = ""
            for key, value in item.items():
                if value:
                    if isinstance(value, list):
                        result += f"{extract_from_list(value)}" + "\n"
                    elif isinstance(value, dict):
                        result += f"{extract_from_dict(value)}" + "\n"
                    elif isinstance(value, str):
                        if "Type" in key:
                            result += "Type: "
                        elif "LimitsAndExceptions" in key:
                            result += "Limits and Exceptions: "
                        result += f"{extract_from_string(value)}\n"
            return result

        output_data = {}
        benefit_id = self.data["BenefitPlan"].get("BenefitPlanID")
        text = ""
        section_name = "Policy Data"

        for item in self.data["BenefitPlan"]["BenefitPlanCSRSection"]["BenefitPlanCSR"]:
            text += item["BenefitPlanCSRName"] + "\n"
            for information in item["BenefitPlanCSRInformation"]:
                description = information["BenefitPlanCSRInformationTypeLanguageDescription"]
                text += DefaultHtmlIngestor.extract_from_html_using_markdownify(description) + "\n"
            text += "\n\n"
        output_data[(benefit_id, section_name)] = text

        for item in self.data["BenefitPlan"]["BenefitPlanCostShareSections"]["PlanCostShareSection"]:
            section_name = item.get("PlanCostShareSectionName")
            text = f"{section_name}\n"
            if section_name:
                if item.get("PlanCostShare"):
                    text += extract_from_list(item["PlanCostShare"])
                if item.get("PlanCostShareCSR"):
                    text += extract_from_list(item["PlanCostShareCSR"])

            if (benefit_id, section_name) not in output_data:
                output_data[(benefit_id, section_name)] = text
            else:
                print(section_name)

        for item in self.data["BenefitPlan"]["BenefitPlanSections"]["BenefitSection"]:
            section_name = item.get("BenefitSectionName")
            text = f"{section_name}\n"
            if section_name:
                if item.get("Benefit"):
                    text += extract_from_list(item["Benefit"])
                if item.get("BenefitCSR"):
                    text += extract_from_list(item["BenefitCSR"])

            if (benefit_id, section_name) not in output_data:
                output_data[(benefit_id, section_name)] = text
            else:
                print(section_name)
        deductibles_text = output_data.get((benefit_id, "Deductibles"))
        for benefit_id, section_name in output_data:
            if section_name != "Deductibles":
                output_data[(benefit_id, section_name)] += deductibles_text
        return output_data

# ------------------------------------------------------------------

METADATA_CREATOR_MAP = {
    "default": DefaultJsonMetadataCreator,
    "kc": CustomJsonMetadataCreatorOne,
    "b360": CustomJsonMetadataCreatorTwo,
    "b360_new": CustomJsonMetadataCreatorThree,
}

CHUNKER_MAP = {
    "default": DefaultJsonChunker,
    "kc": CustomJsonChunkerOne,
    "b360": CustomJsonChunkerTwo,
    "b360_new": CustomJsonChunkerThree,
}


class JsonExtractor(BaseExtractor):
    """Extractor class of textual data from JSON files and chunks sections into separate files.

    This class inherits from the `BaseExtractor` and provides specialized
    functionality for extracting text content from .docx documents.

    Args:
        filepath (str): The path to the .docx file.
        config_file_parameters (dict[str, str]): Configuration settings for the
          extraction process.

    Attributes:
        filepath (str): Stores the path to the input file.
        config_file_parameters (dict[str, str]): Stores the configuration
          parameters.
        json_extraction (str): Configuration parameter fot the extraction
          method. Defaults to "default".
        json_chunking (str):  Configuration parameter fot the chunking method.
          Defaults to "default".
    """

    def __init__(self, filepath: str, config_file_parameters: dict[str, str]):
        super().__init__(filepath, config_file_parameters)
        self.json_extraction = config_file_parameters.get(
            "json_extraction", "default"
        )
        self.json_chunking = config_file_parameters.get(
            "json_chunking", "default"
        )
        self.data = None

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
            if not bool(re.search(r"[a-zA-Z0-9]", context)):
                continue
            context = re.sub(r'(\s)\1+', r'\1', context)
            with open(filepath + ".txt", "w", encoding="utf-8") as f:
                f.write(context)
            temp_metadata = metadata.copy()
            temp_metadata.pop("filename")
            temp_metadata["section_name"] = section_name.lower()
            if section_id and isinstance(section_id, str):
                temp_metadata["benefit_id"] = section_id.lower()

            with open(filepath + "_metadata.json", "w", encoding="utf-8") as f:
                json.dump(temp_metadata, f)
        return True

    def process(self, output_dir: str) -> bool:
        """
        Main function that controls the processing of a JSON document, including extraction,
        metadata creation, chunking, and file saving.

        This function coordinates the key steps for processing a JSON document.
        It handles document extraction, metadata generation, applies  document
        chunking strategies, and saves the resulting chunks and metadata to
        files.

        Args:
            output_dir (str): The directory where the processed files should be
              saved.

        Returns:
            bool: True if the document processing was successful, False
            otherwise.
        """
        extractor = DefaultJsonExtractor(self.filepath)
        self.data = extractor.extract_document()
        if self.json_chunking == "custom":
            kc_name = re.match(r"^KM\d{7}\.json", os.path.basename(self.filepath))
            if "BenefitPlan" in self.data and not kc_name:
                chunking = "b360_new"
            else:
                chunking = "kc"
            config_file_parameters = copy.deepcopy(self.config_file_parameters)
            config_file_parameters["json_chunking"] = chunking
            extractor = JsonExtractor(self.filepath, config_file_parameters)
            return extractor.process(output_dir)

        # for b360 use loop
        elif self.json_chunking == "b360":
            for category_data in self.data["benefits"]:
                metadata_creator = METADATA_CREATOR_MAP.get(
                    self.json_chunking, DefaultJsonMetadataCreator
                )(self.filepath, category_data)
                metadata = metadata_creator.create_metadata()
                if not metadata:
                    return False

                document_chunker = CHUNKER_MAP.get(
                    self.json_chunking, DefaultJsonChunker
                )(self.filepath, category_data)
                document_chunks = document_chunker.chunk_the_document()
                if not self.create_files(document_chunks, metadata, output_dir):
                    return False
        elif self.json_chunking == "b360_new":
            metadata_creator = METADATA_CREATOR_MAP.get(
                self.json_chunking, DefaultJsonMetadataCreator
            )(self.filepath, self.data)
            metadata = metadata_creator.create_metadata()
            if not metadata:
                return False

            document_chunker = CHUNKER_MAP.get(
                self.json_chunking, DefaultJsonChunker
            )(self.filepath, self.data)
            document_chunks = document_chunker.chunk_the_document()
            if not self.create_files(document_chunks, metadata, output_dir):
                return False
        else:
            metadata_creator = METADATA_CREATOR_MAP.get(
                self.json_chunking, DefaultJsonMetadataCreator
            )(self.filepath, self.data)
            metadata = metadata_creator.create_metadata()
            if not metadata:
                return False

            document_chunker = CHUNKER_MAP.get(
                self.json_chunking, DefaultJsonChunker
            )(self.filepath, self.data, self.config_file_parameters)
            document_chunks = document_chunker.chunk_the_document()
            if not document_chunks:
                return False
            if not self.create_files(document_chunks, metadata, output_dir):
                return False
        return True
