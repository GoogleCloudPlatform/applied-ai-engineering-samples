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
from unittest.mock import mock_open, patch

from gen_ai.extraction_pipeline.document_extractors.docx_extractor import DocxExtractor
from gen_ai.extraction_pipeline.document_extractors.xml_extractor import XmlExtractor


# def test_modify_file_positive():
#     """
#     Tests that the `XmlExtractor.modify_file()` method correctly updates the contents of
#     an XML file with specific process group information.

#     Key Verifications:
#         File Opening:
#                 Confirms that the file is opened in both read ("r" - to check the file)
#                 and write ("w" - to modify the file) modes.
#         Expected Structure:
#             Ensures the following lines are written to the file:
#                 "<ProcessGroup Name="{filename}">\n" (Including the correct filename)
#                 "<ProcessGroupItems>\n"
#                 "</ProcessGroupItems>\n"
#                 "</ProcessGroup>\n"
#     """
#     filename = "test_file.xml"
#     extractor = XmlExtractor(filename, {})
#     with patch("builtins.open", mock_open(read_data="test data")) as mocked_file:
#         extractor.modify_file()
#     mocked_file.assert_any_call("test_file.xml", "r")
#     mocked_file.assert_called_with("test_file.xml", "w")
#     mocked_file().write.assert_any_call(f'<ProcessGroup Name="{filename}">\n')
#     mocked_file().write.assert_any_call("<ProcessGroupItems>\n")
#     mocked_file().write.assert_any_call("</ProcessGroupItems>\n")
#     mocked_file().write.assert_any_call("</ProcessGroup>\n")


# def test_modify_file_negative():
#     """
#     Tests that the `XmlExtractor.modify_file()` method does not attempt to write to a file
#     if proper xml tags are already in the file.

#     Key Verifications:
#         Ensures that the file is opened only once in read ('r') mode. The absence of a write ('w') mode call indicates that modification is not attempted.
#     """

#     filename = "test_file.xml"
#     extractor = XmlExtractor(filename, {})
#     with patch("builtins.open", mock_open(read_data="test test_file.xml")) as mocked_file:
#         extractor.modify_file()
#     mocked_file.assert_called_once_with("test_file.xml", "r")


# def test_xml_create_metadata():
#     """
#     Tests that the `XmlExtractor.create_metadata()` method correctly generates a JSON
#     metadata file containing information extracted from a key, value, and filepath.

#     Key Verifications:
#         Metadata File Creation:
#             Ensures that a correct file name is created from provided data ('test_file_metadata.json') and the file is opened in write ('w') mode.
#         Metadata Content:
#             Asserts that the right data is written into the file: section id; group; document name; section name; and filename.
#     """
#     filename = "test_file.xml"
#     extractor = XmlExtractor(filename, {})

#     key = f" --- {filename} --- Bakery --- Code Control --- Action Markdowns"
#     value = ("4296", "Code Control", "")
#     filepath = "test_file"
#     with patch("builtins.open", mock_open()) as mocked_file:
#         extractor.create_metadata(key, value, filepath)
#     mocked_file.assert_called_with("test_file_metadata.json", "w")

#     mocked_file().write.assert_any_call(f'"{value[0]}"')
#     mocked_file().write.assert_any_call(f'"{value[1]}"')
#     mocked_file().write.assert_any_call(f'"{key.split(" --- ")[2]}"')
#     mocked_file().write.assert_any_call(f'"{" ".join(key.split(" --- ")[2:]).lower()}"')
#     mocked_file().write.assert_any_call(f'"{filename}"')


# def test_xml_create_file():
#     """
#     Tests that the `XmlExtractor.create_file()` method correctly generates text and metadata files in the specified output directory, using information derived from the provided content.

#     Key Verifications:
#         Text File Creation: Ensures that a text file is created within the 'output_dir' with a name derived from elements of the section names. The file extension is '.txt'.
#         Metadata File Creation: Ensures that a JSON metadata file is created with a similar naming convention with the extension '.json'.
#         Text File Content: Asserts that the provided page content is written into the text file.
#     """
#     filename = "test_file.xml"
#     extractor = XmlExtractor(filename, {})

#     key = f" --- {filename} --- Bakery --- Code Control --- Action Markdowns"
#     value = ("4296", "Code Control", "Some page content")
#     content = {key: value}
#     output_dir = "output_dir"

#     with patch("builtins.open", mock_open()) as mocked_file:
#         extractor.create_file(content, output_dir)

#     mocked_file.assert_any_call("output_dir/se_test_file_xml_bakery_code_control_action_markdowns.txt", "w")
#     mocked_file.assert_called_with(
#         "output_dir/se_test_file_xml_bakery_code_control_action_markdowns_metadata.json", "w"
#     )

#     mocked_file().write.assert_any_call(f"{value[2]}")


# def test_docx_create_filepath():
#     """
#     Tests that the `DocxExtractor.create_filepath()` method generates a valid output
#     filepath for a text file extracted from a DOCX document.

#     Key Verifications:
#         Base Filename: Uses the 'filename' value from the 'metadata' dictionary.
#         Section Name Processing:
#             Replaces spaces with underscores ('_').
#             Removes special characters (e.g., '*', '/', '$', '-')
#             Converts the section name to lowercase.
#         Output Directory: Ensures the constructed filepath includes the specified output_dir.
#     """
#     filename = "test_file.docx"
#     extractor = DocxExtractor(filename, {})

#     metadata = {"filename": "test_filename.txt"}
#     section_name = "Introduction & into ___ the /*$ - SectIonS_"
#     output_dir = "output_dir"

#     expected_filepath = "output_dir/test_filename-introduction_into_the_-_sections"
#     filepath = extractor.create_filepath(metadata, section_name, output_dir)

#     assert filepath == expected_filepath


# def test_docx_create_files():
#     """
#     Tests that the `DocxExtractor.create_files()` method correctly generates text files
#     from extracted DOCX content, storing them in the specified output directory.

#     Key Verifications:
#         File Creation: Ensures that a text file is created for each section present in
#                         the 'document_chunks' dictionary. The filenames are derived from
#                         the metadata's 'filename' and the section names.
#         File Content: Asserts that the section content associated with each section name in the 'document_chunks' is written into the corresponding text file.
#     """
#     filename = "test_file.docx"
#     extractor = DocxExtractor(filename, {})

#     metadata = {"filename": "test_filename.txt"}
#     key = ("4296", "Section One")
#     value = "Page content"
#     document_chunks = {key: value}
#     output_dir = "output_dir"

#     with patch("builtins.open", mock_open()) as mocked_file:
#         extractor.create_files(document_chunks, metadata, output_dir)
#     mocked_file.assert_any_call("output_dir/test_filename-section_one.txt", "w")
#     mocked_file().write.assert_any_call(f"{value}")
