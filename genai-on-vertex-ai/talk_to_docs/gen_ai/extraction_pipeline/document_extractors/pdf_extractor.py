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
Provides the PdfExtractor class for extracting textual data from PDF files and organizing the extracted data
into separate files for structured document processing.
"""

import json
import os
import re

from gen_ai.extraction_pipeline.document_extractors.base_extractor import BaseExtractor
from gen_ai.extraction_pipeline.document_extractors.docai_pdf_extraction import process_document_in_chunks
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import VertexAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from unstructured.chunking.basic import chunk_elements
from unstructured.chunking.title import chunk_by_title
from unstructured.documents.elements import Text
from unstructured.partition.pdf import partition_pdf


class PdfExtractor(BaseExtractor):
    """Extractor class of textual data from pdf files and chunks sections into separate files.

    This class inherits from the `BaseExtractor` and provides specialized
    functionality for extracting text content from pdf documents.

    Args:
        filepath (str): The path to the .docx file.
        config_file_parameters (dict[str, str]): Configuration settings for the
          extraction process.

    Attributes:
        filepath (str): Stores the path to the input file.
        config_file_parameters (dict[str, str]): Stores the configuration
          parameters.
        pdf_extraction (str): Configuration parameter fot the extraction method.
          Defaults to 'default'.
        pdf_chunking (str):  Configuration parameter fot the chunking method.
          Defaults to 'default'.
    """

    def __init__(self, filepath: str, config_file_parameters: dict[str, str]):
        super().__init__(filepath, config_file_parameters)
        self.pdf_extraction = config_file_parameters.get(
            "pdf_extraction", "default"
        )
        self.pdf_chunking = config_file_parameters.get(
            "pdf_chunking", "default"
        )
        self.elements = None

    def create_filepath(
        self, metadata: dict[str, str], section_name: str, output_dir: str
    ) -> str:
        """Creates a file-system-friendly path for saving a document section.

        * Removes extension of the filename
        * Removes leading digits, whitespace, and hyphens from the section name.
        * Condenses multiple underscores into single underscores.

        Args:
            metadata (dict[str, str]): A dictionary containing document
              metadata, including a 'filename' key.
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
            temp_metadata["section_name"] = section_name.lower()

            with open(filepath + "_metadata.json", "w", encoding="utf-8") as f:
                json.dump(temp_metadata, f)
        return True

    def process(self, output_dir: str) -> bool:
        """
        Main function that controls the processing of a .pdf document, including extraction, metadata creation,
        chunking, and file saving.

        This function coordinates the key steps for processing a .pdf document.
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
        if self.pdf_extraction == "with_tables":
            extractor = DefaultPdfExtractor(self.filepath)
            self.elements = extractor.extract_document(self.config_file_parameters)
        elif self.pdf_extraction == "docai":
            extractor = DocaiPdfExtractor(self.filepath)
            self.elements = extractor.extract_document(self.config_file_parameters)[0]
        else:
            extractor = DefaultPdfExtractor(self.filepath)
            self.elements = extractor.extract_document()
        if not self.elements:
            return False

        metadata_creator = DefaultPdfMetadataCreator(self.filepath)
        metadata = metadata_creator.create_metadata()
        if not metadata:
            return False

        if self.pdf_chunking == "by_title":
            document_chunker = DefaultPdfChunker(self.elements, by_title=True)
        elif self.pdf_chunking == "semantic":
            if self.pdf_extraction != "default" and self.pdf_extraction != "with_tables":
                print("Semantic chunking is only for unstructured extraction (default or with_tables)")
                return False
            whole_document_text = " \n".join(
                [el.text for el in self.elements if el.category not in ("Footer", "Header")]
            )
            document_chunker = SemanticPdfChunker(whole_document_text, "textembedding-gecko@003")
        elif self.pdf_chunking == "docai":
            document_chunker = DocaiPdfChunker(self.elements, chunk_size=1000, overlap=100)
        else:
            document_chunker = DefaultPdfChunker(
                self.elements, chunk_size=1000, overlap=100, overlap_all=False
            )

        document_chunks = document_chunker.chunk_the_document()
        if not document_chunks:
            return False
        if self.create_files(document_chunks, metadata, output_dir):
            return True
        return False


class DefaultPdfExtractor:
    """Default extractor class that provides methods for extracting content from .pdf files.

    Args:
        filepath (str): The path to the pdf file.

    Attributes:
        filepath (str): The path to the pdf file.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

    def extract_using_unstructured(self, strategy: str) -> list[Text]:
        hi_res_model_name = "yolox" if strategy == "hi_res" else None
        return partition_pdf(
            self.filepath,
            strategy=strategy,
            hi_res_model_name=hi_res_model_name,
            url=None,
        )

    def extract_document(self, config: dict[str, str] = None) -> list[Text]:
        """Extracts the Document object from the pdf file.

        Args:
            config (dict[str, str], optional): A dictionary containing configuration options.
                Defaults to None.

        Returns:
            list[Text]: A list of extracted Text objects representing the textual content of the PDF.
        """
        if config and config.get("pdf_extraction") == "with_tables":
            return self.extract_using_unstructured(strategy="hi_res")
        return self.extract_using_unstructured(strategy="fast")


class DocaiPdfExtractor(DefaultPdfExtractor):
    """Extractor class that provides methods for extracting content using DocAI from .pdf files.

    Args:
        filepath (str): The path to the pdf file.

    Attributes:
        filepath (str): The path to the pdf file.
    """

    def extract_document(self, config: dict[str, str] = None) -> list[str]:
        """Extracts the Document object from the pdf file.
        Args:
            config (dict[str, str], optional): A dictionary containing configuration options.
                Defaults to None.

        Returns:
            list[Text]: A list of extracted strings representing the textual content of the PDF.
        """
        return process_document_in_chunks(self.filepath, config)


class DefaultPdfMetadataCreator:
    """Default class for creating metadata from .docx files.

    Provides a basic metadata structure including the filename.

    Args:
        filepath (str): The path to the .docx file.

    Attributes:
        filename (str): The name of the .docx file (without the path).
    """

    def __init__(self, filepath: str):
        filename = os.path.basename(filepath)
        self.filename = filename

    def create_metadata(self) -> dict[str, str]:
        """A method to be implemented by subclasses.

        Generates a dictionary of metadata extracted from the .docx file.

        Returns:
            dict[str, str]: A dictionary containing metadata keys and their
            corresponding values.
        """
        metadata = {
            "filename": self.filename,
        }
        return metadata


class DefaultPdfChunker:
    """Default chunker class that provides the structure for extracting sections and chunking .docx documents.

    This class defines the core framework for working with documents, section
    identification, and text chunking.

    Attributes:
        elements (list[Text | str]): The raw text content extracted from the pdf
          document.
    """

    def __init__(
        self,
        elements: list[Text | str],
        by_title: bool = False,
        chunk_size: int = 500,
        overlap: int = 0,
        overlap_all: bool = False,
    ):
        self.elements = elements
        self.by_title = by_title
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.overlap_all = overlap_all

    def chunk_the_document(self) -> dict[tuple[str, str], str]:
        """Divides the .docx document into chunks based on the defined sections names.

        Returns:
            dict[tuple[int, str], str]: A dictionary where the keys are tuples
            of (section_id, section_title) and the values are the corresponding
            text chunks.
        """
        if self.by_title:
            chunks = chunk_by_title(self.elements)
        else:
            chunks = chunk_elements(
                self.elements,
                max_characters=self.chunk_size,
                overlap=self.overlap,
                overlap_all=self.overlap_all,
            )

        return {(chunk.id, chunk.id): chunk.text for chunk in chunks}


class DocaiPdfChunker(DefaultPdfChunker):
    """Splits PDF text content into chunks for processing by DocAI models.

    This class extends the 'DefaultPdfChunker' and leverages the
    'RecursiveCharacterTextSplitter' to divide PDF document text into
    manageable chunks, ensuring efficient processing.

    Args:
        elements: A list of strings, where each string represents text content
          from a PDF page.
        chunk_size: (Optional) The desired maximum size of each chunk (in
          characters). Defaults to 500.
        overlap: (Optional) The number of overlapping characters between
          consecutive chunks. Defaults to 0.

    Attributes:
        elements: Text content of the PDF page.
        chunk_size: The maximum size of each chunk.
        overlap: The number of overlapping characters between chunks.
    """

    def __init__(
        self, elements: list[str], chunk_size: int = 500, overlap: int = 0
    ):
        super().__init__(
            elements=elements, chunk_size=chunk_size, overlap=overlap
        )

    def chunk_the_document(self) -> dict[tuple[str, str], str]:
        """Splits the text from the input PDF documents into chunks and returns a dictionary.

        Returns:
            dict[tuple[str, str], str]: A dictionary of text chunks with their
            identifiers.
        """

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.overlap,
        )

        output_chunks = {}
        for doc in self.elements:
            chunks = text_splitter.split_text(doc)
            doc_name = doc.split("\n")[0]
            for i in range(len(chunks)):
                chunk_id = f"{doc_name}_{i}"
                output_chunks[(chunk_id, chunk_id)] = chunks[i]
        return output_chunks


class SemanticPdfChunker(DefaultPdfChunker):
    """Splits PDF text content into semantic chunks for.

    This class extends the 'DefaultPdfChunker' and leverages the
    'RecursiveCharacterTextSplitter' to divide PDF document text into
    manageable chunks, ensuring efficient processing.

    Args:
        elements: A list of strings, where each string represents text content
          from a PDF page.
        model_name: str: (Optional) The Embedding model name to use in 
          semantic chunking. Defaults to "textembedding-gecko@003".

    Attributes:
        elements: Text content of the PDF page.
        model_name: Embedding model name to use in semantic chunking.
    """

    def __init__(
        self, elements: list[str], model_name: str = "textembedding-gecko@003"
    ):
        super().__init__(
            elements=elements
        )
        self.embedding = VertexAIEmbeddings(model_name=model_name)

    def chunk_the_document(self) -> dict[tuple[str, str], str]:
        """Splits the text from the input PDF documents into chunks and returns a dictionary.

        Returns:
            dict[tuple[str, str], str]: A dictionary of text chunks with their
            identifiers.
        """
        text_splitter = SemanticChunker(self.embedding)
        output_chunks = {}

        for doc in [self.elements]:
            chunks = text_splitter.split_text(doc)
            doc_name = doc.split("\n")[0]
            for i in range(len(chunks)):
                chunk_id = f"{doc_name}_{i}"
                output_chunks[(chunk_id, chunk_id)] = chunks[i]
        return output_chunks
