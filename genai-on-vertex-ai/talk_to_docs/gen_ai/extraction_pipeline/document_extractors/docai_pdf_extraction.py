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
This module provides functions for processing PDF documents using Google Document AI, enabling 
efficient extraction and structuring of textual and tabular data from PDF files.
"""

from io import BytesIO
import traceback
from typing import Optional, Sequence

from google.api_core.client_options import ClientOptions
from google.cloud import documentai
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter


def extract_pdf_chunk(pdf_reader: PdfReader, start_page: int, end_page: int) -> bytes:
    """
    This method takes in a PdfReader object and get the contents of the BytesIO object 
    written from the specified page number range.

    Arguments:
        pdf_reader {PyPDF2.PdfReader} -- The PdfReader object to get the chunk from.
        start_page {int} -- The page number where the PDF chunk starts.
        end_page {int} -- The page number for the last page of the PDF chunk.

    Returns:
        bytes -- PDF chunk content in bytes.
    """

    try:
        writer = PdfWriter()

        for page_number in range(start_page - 1, end_page):
            writer.add_page(pdf_reader.pages[page_number])

        chunk_pdf_content = BytesIO()
        writer.write(chunk_pdf_content)
        chunk_pdf_content.seek(0)
    except Exception as e: # pylint: disable=W0718
        # Handle the exception here
        traceback.print_exc()
        print("An error occurred:", str(e))

    return chunk_pdf_content.getvalue()


def list_blocks(
        blocks: Sequence[documentai.Document.Page.Block],
        text: str, page_number: int
) -> list[list[list[str, float, int]]]:
    """
    Categorizes blocks of text from a page into left and right margin blocks based on their horizontal position.

    Args:
        blocks: A sequence of Document.Page.Block objects representing blocks of text on a page.
        text: The full text content of the page.
        page_number: The page number from which the blocks are extracted.

    Returns:
        A list containing two lists:
            - The first list contains information about blocks located within the left margin.
            - The second list contains information about blocks located outside the left margin.

        Each inner list contains entries representing individual blocks, where each entry is itself a list containing:
            - The text content of the block.
            - The minimum normalized y-coordinate of the block's bounding polygon (indicating its vertical position).
            - The page number from which the block originates.
    """
    margin = 0.5
    block_list = [[], []]
    for block in blocks:
        block_text = layout_to_text(block.layout, text)
        if all(x.x < margin for x in block.layout.bounding_poly.normalized_vertices):
            block_list[0].append(
                [
                    block_text,
                    min(y.y for y in block.layout.bounding_poly.normalized_vertices),
                    page_number,
                ]
            )
        else:
            block_list[1].append(
                [
                    block_text,
                    min(y.y for y in block.layout.bounding_poly.normalized_vertices),
                    page_number,
                ]
            )
    return block_list


def process_document(
    pdf_reader: PdfReader,
    start_page: int,
    end_page: int,
    config: dict[str, str],
    process_options: Optional[documentai.ProcessOptions] = None,
) -> documentai.Document:
    """
    Process a range of pages from a PDF document using Document AI and return the Document object
    with all its metadata.

    Arguments:
        pdf_reader {PdfReader} -- A PDF reader object.
        start_page {int} -- The starting page number to process.
        end_page {int} -- The ending page number to process.
        config {dict[str, str]} -- Configuration parameters necessary for DocAI
        process_options {documentai.ProcessOptions} -- An optional field to set config for DocOCR.
        
    Returns:
        documentai.Document: The processed Document AI document, or None if an error occurs.
    """
    project_id = config.get("docai_project_id")
    location = config.get("docai_location")
    mime_type = "application/pdf"
    processor_id = config.get("docai_dococr_processor_id")
    processor_version = config.get("docai_dococr_processor_version")

    try:
        # You must set the `api_endpoint` if you use a location other than "us".
        client = documentai.DocumentProcessorServiceClient(
            client_options=ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        )

        name = client.processor_version_path(project_id, location, processor_id, processor_version)

        # Extract the relevant pages for the current chunk
        chunk_pdf_content = extract_pdf_chunk(pdf_reader, start_page, end_page)

        # Load Binary Data into Document AI RawDocument Object
        raw_document = documentai.RawDocument(content=chunk_pdf_content, mime_type=mime_type)

        print(f"About to process {start_page} - {end_page}")
        # Configure the process request
        request = documentai.ProcessRequest(
            name=name,
            raw_document=raw_document,
            # Only supported for Document OCR processor
            process_options=process_options,
        )

        result = client.process_document(request=request)
    except Exception as e: # pylint: disable=W0718
        # Handle the exception here
        traceback.print_exc()
        print(f"An error occurred while processing pages {start_page} to {end_page}:", str(e))
        return None
    return result.document


def layout_to_text(layout: documentai.Document.Page.Layout, text: str) -> str:
    """
    Extracts and concatenates text segments from a Document AI layout into a single string.

    Args:
        layout (documentai.Document.Page.Layout): The layout object containing information about text segments 
        and their offsets within the document.
        text (str): The entire text content of the document.

    Returns:
        str: The concatenated text extracted from the layout, representing the textual content identified within 
             the specified layout.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in layout.text_anchor.text_segments:
        start_index = int(segment.start_index)
        end_index = int(segment.end_index)
        response += text[start_index:end_index]
    return response


def extract_text_data(page: documentai.Document.Page, text: str) -> tuple[list[list[str]], list[int]]:
    """
    Extracts textual data from a Document AI page, separating table data from non-table text lines.
    The function processes the page's tables, identifies their dimensions, and extracts their content.
    It then distinguishes text lines that are not part of any table and sorts both tables and text lines based 
    on their vertical position.


    Args:
        page: A Document AI Page object containing the page's layout and content.
        text: The raw text extracted from the document.

    Returns:
        A tuple containing:
            - sorted_tables: A list of sorted tables, each represented as a list of table rows (lists of strings).
            - sorted_text_lines_only: A list of sorted text lines not belonging to any table, along with their
              coordinates and original line index.
    """
    all_table_cells = {}
    all_table_rows = {}
    table_info = []
    sorted_table_info = []
    table_dimensions = []
    sorted_tables = []

    for i, table in enumerate(page.tables):
        # getting min and max  x,y coordinates for the table
        min_x, min_y, max_x, max_y = table_coordinates(table)
        dimensions = (min_x, min_y, max_x, max_y)

        table_cells = []
        table_rows = []
        for table_row in table.header_rows:
            process_table_row(text, table_cells, table_rows, table_row)
        for table_row in table.body_rows:
            process_table_row(text, table_cells, table_rows, table_row)
        all_table_cells[i] = table_cells
        all_table_rows[i] = table_rows

        table_info.append((table_rows, dimensions, i))

    # sort the tables based on the min_y coordinate
    sorted_table_info = sorted(table_info, key=lambda x: x[1][1])
    for stl in sorted_table_info:
        sorted_tables.append((stl[0], stl[1][0], stl[1][1], stl[2]))
    # list of coordinates for all tables
    table_dimensions = [element[1] for element in sorted_table_info]

    text_lines_only = []
    sorted_text_lines_only = []
    for l, line in enumerate(page.lines):
        line_in_text_block = False
        for td in table_dimensions:
            # check if line is inside a table
            if is_line_inside_current_text_block(line, td):
                line_in_text_block = True
                break
        # append the line once you confirm its not part of a table
        if line_in_text_block is False:
            text_lines_only.append(
                (
                    layout_to_text(line.layout, text),
                    line.layout.bounding_poly.vertices[0].x,
                    line.layout.bounding_poly.vertices[0].y,
                    l,
                )
            )
    sorted_text_lines_only = sorted(text_lines_only, key=lambda x: (50 * x[2] + x[1]))

    return sorted_tables, sorted_text_lines_only


def is_line_inside_current_text_block(line: str, td: list) -> bool:
    """
    Determines if a given text line is located within the current text block.

    Args:
        line: A text line object containing layout information and bounding polygon coordinates.
        td: A tuple representing the coordinates of the current text block, likely (top, left, bottom, right).

    Returns:
        bool: True if the line is within the text block, False otherwise.
    """

    return (
        line.layout.bounding_poly.vertices[0].y >= td[1]
        and line.layout.bounding_poly.vertices[0].y <= td[3]
    )


def table_coordinates(table: documentai.Document.Page.Table) -> tuple[float, float, float, float]:
    """
    Calculates the minimum and maximum x and y coordinates of a table's bounding box.

    Args:
        table: The table object containing layout information with bounding_poly.

    Returns:
        A tuple containing four values:
        - min_x: The minimum x-coordinate of the table's bounding box.
        - min_y: The minimum y-coordinate of the table's bounding box.
        - max_x: The maximum x-coordinate of the table's bounding box.
        - max_y: The maximum y-coordinate of the table's bounding box.
    """

    min_x, min_y = float("inf"), float("inf")
    max_x, max_y = float("-inf"), float("-inf")
    table_x = [table.layout.bounding_poly.vertices[x].x for x in range(4)]
    table_y = [table.layout.bounding_poly.vertices[y].y for y in range(4)]
    for j in range(4):
        min_x = min(min_x, table_x[j])
        min_y = min(min_y, table_y[j])
        max_x = max(max_x, table_x[j])
        max_y = max(max_y, table_y[j])
    return min_x, min_y, max_x, max_y


def process_table_row(
    text: str,
    table_cells: list[str],
    table_rows: list[str],
    table_row: documentai.Document.Page.Table.TableRow,
):
    """
    Extracts text from each cell of a table row, appends it to `table_cells`,
    and constructs a row string which is then appended to `table_rows`.

    Args:
        text (str): The full text content of the document.
        table_cells (list[str]): A list to store extracted cell text.
        table_rows (list[str]): A list to store extracted row text.
        table_row (documentai.Document.Page.Table.TableRow): A table row object.

    Returns:
        None: This function modifies `table_cells` and `table_rows` in-place.
    """
    row_text = ""
    for cell in table_row.cells:
        cell_text = layout_to_text(cell.layout, text)
        table_cells.append(cell_text)
        row_text += cell_text
    table_rows.append(row_text.strip())


def convert_table_to_dataframe(table: documentai.Document.Page.Table, text: str) -> str:
    """
    Converts a structured table object (with header and body rows) into a Pandas DataFrame, 
    then to a LaTeX table string.

    Args:
        table: The table object containing header_rows and body_rows, each row consisting of cells with layouts.
        text: The associated text from which the table layout was extracted (used in `layout_to_text`).

    Returns:
        A string representing the table in LaTeX format, ready for inclusion in LaTeX documents.
    """
    rows = []

    for table_row in table.header_rows:
        row = [layout_to_text(cell.layout, text).strip() for cell in table_row.cells]
        header = row
        rows.append(row)

    for table_row in table.body_rows:
        row = [layout_to_text(cell.layout, text).strip() for cell in table_row.cells]
        rows.append(row)

    # Convert rows into dataframe
    dataframe = pd.DataFrame(rows, columns=header)
    dataframe = dataframe.drop(0)
    latex_table = dataframe.style.to_latex()

    return latex_table


def process_chunk(document: documentai.Document) -> list[str]:
    """
    Read the contents of the document from DocAI's Document object and sort it according to
    their y-coordinate values to get it line-by-line.

    Args:
        chunk_index {int} -- Integer index of the current chunk.
        chunk-size {int} -- The size limit of a chunk in pages. For DocAI, it is 15.
        document {documentai.Document} -- DocAI's document object.

    Returns:
        list[str] -- A list of strings after processing and sorting.
    """
    output = []
    try:
        text = document.text
        for page in document.pages:
            page_text = ""
            # Get the text data in the page in the form of a list of text blocks.
            tables, lines = extract_text_data(page, text)

            remaining_tables = len(tables)
            remaining_lines = len(lines)

            while remaining_tables > 0 or remaining_lines > 0:
                if remaining_tables > 0 and remaining_lines > 0:
                    if lines[0][2] < tables[0][2]:
                        remaining_lines, page_text = transfer_line_to_output(page_text, lines, remaining_lines)
                    else:
                        remaining_tables, page_text = transfer_table_to_output(
                            text,
                            page_text,
                            page,
                            tables,
                            remaining_tables
                        )
                elif remaining_tables == 0:
                    while remaining_lines > 0:
                        remaining_lines, page_text = transfer_line_to_output(page_text, lines, remaining_lines)
                else:
                    while remaining_tables > 0:
                        remaining_tables, page_text = transfer_table_to_output(
                            text,
                            page_text,
                            page,
                            tables,
                            remaining_tables
                        )
            output.append(page_text.replace("\\n", "\n"))

    except Exception as e: # pylint: disable=W0718
        # Handle the exception here
        traceback.print_exc()
        print("An error occurred:", str(e))
    return output


def process_blocks(chunk_index: int, chunk_size: int, document: documentai.Document) -> list[list[list[str]]]:
    """
    Processes blocks of text within a document and organizes them into tables and paragraphs.

    Args:
        chunk_index: The index of the current chunk being processed.
        chunk_size: The number of pages in each chunk.
        document: A DocumentAI Document object containing the text to be processed.

    Returns:
        A list containing two lists:
            - The first list contains extracted tables.
            - The second list contains extracted paragraphs.
    """
    output = [[], []]
    try:
        text = document.text

        for page in document.pages:
            page_number = page.page_number + chunk_index * chunk_size
            blocks = list_blocks(page.blocks, text, page_number)
            output[0].extend(blocks[0])
            output[1].extend(blocks[1])
    except Exception as e: # pylint: disable=W0718
        # Handle the exception here
        traceback.print_exc()
        print("An error occurred:", str(e))
    return output


def transfer_table_to_output(
        text: str,
        output: str,
        page: documentai.Document.Page,
        tables: list,
        remaining_tables: int
) -> tuple[int, str]:
    """
    Extracts a table from a list of tables, converts it to a DataFrame, appends the DataFrame to an output 
    string, and decrements a counter.

    Args:
        text (str): The text containing the tables.
        output (str): The output string to which the table will be appended.
        page: An object representing the page containing the tables (assumed to have a 'tables' attribute).
        tables (list): A list of table descriptors (assumed to contain tuples with table information).
        remaining_tables (int): A counter representing the number of tables remaining to be processed.

    Returns:
        tuple: A tuple containing the updated counter `m` and the updated output string `output`.
    """
    curr_table = tables.pop(0)
    dataframe = convert_table_to_dataframe(page.tables[curr_table[3]], text)
    output += f" \nTable: {dataframe}\n"
    remaining_tables -= 1
    return remaining_tables, output


def transfer_line_to_output(output: str, lines: list[str], remaining_lines: int) -> tuple[int, str]:
    """
    Transfers the first line from a list to an output string.

    Args:
        output: The current output string.
        lines: The list of lines to be transferred.
        remaining_lines: The remaining number of lines to be transferred.

    Returns:
        A tuple containing the updated number of remaining lines and the updated output string.
    """
    curr_line = lines.pop(0)
    output += curr_line[0]
    remaining_lines -= 1
    return remaining_lines, output


def gs_bucket_bypass(
    pdf_reader: PdfReader,
    process_options: documentai.ProcessOptions,
    output: list,
    blocks: list[list],
    start_page: int,
    end_page: int,
    chunk_index: int,
    chunk_size: int,
    config: dict[str, str]
) -> list[str]:
    """
    This is a method designed for testing purpose. This avoids the storage-and-retrieval part
    from the normal pipeline but does the same processing on each chunk.

    Args:
        pdf_reader {PyPDF2.PdfReader} -- PdfReader object to get the raw text from.
        process_options {documentai.ProcessOptions} -- An optional field to set config for DocOCR.
        output {list} -- List of strings containing extraction text till the previous chunk.
        blocks {list{list}} -- Blocks
        start_page {int} -- Starting page index of the chunk to be processed.
        end_page {int} -- Last page index to be considered in the chunk.
        chunk_index {int} -- Integer index of the current chunk.
        chunk_size {int} -- The size limit of a chunk in pages. For DocAI, it is 15.
        config {dict[str, str]} -- Configuration parameters necessary for DocAI

    Returns:
        list[str] -- An updated `output` list with the text output of the current chunk appeneded at
                        the end.
    """

    # Online processing request to Document AI
    document = process_document(
        pdf_reader,
        start_page,
        end_page,
        process_options=process_options,
        config=config,
    )

    if document is not None:
        # Process the current chunk and print the results
        curr_chunk_output = process_chunk(document)
        output += curr_chunk_output
        terms_boxes = process_blocks(chunk_index, chunk_size, document)
        blocks[0].extend(terms_boxes[0])
        blocks[1].extend(terms_boxes[1])

    return output, blocks


def process_document_in_chunks(file_path: str, config: dict[str, str]) -> list[str]:
    """
    This method is the starting point of Argonaut's DocAI-based PDF processing pipeline. Here,
    the document gets split into 15-page chunks and each chunk gets processed one after another.

    Arguments:
        file_path {str} -- Path of the file to be processed.

    Returns:
        list[str] -- A list of strings for each chunk of the document.
    """
    # Process options for DocAI
    process_options = documentai.ProcessOptions(
        ocr_config=documentai.OcrConfig(
            # compute_style_info=True,
            enable_native_pdf_parsing=True,
            enable_image_quality_scores=False,
            enable_symbol=False,
        )
    )

    try:
        # Read the PDF and get the total number of pages
        print("Processing:", file_path.split("/")[-1])
        extracted_text = []
        extracted_blocks = [[], []]
        pdf_reader = None
        with open(file_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()
            pdf_reader = PdfReader(BytesIO(pdf_content))
            num_pages = len(pdf_reader.pages)


        # Split the PDF into chunks of 15 pages
        chunk_size = 15
        num_chunks = (num_pages - 1) // chunk_size + 1

        for chunk_index in range(num_chunks):
            start_page = chunk_index * chunk_size + 1
            end_page = min((chunk_index + 1) * chunk_size, num_pages)
            extracted_text, extracted_blocks = gs_bucket_bypass(
                pdf_reader,
                process_options,
                extracted_text,
                extracted_blocks,
                start_page,
                end_page,
                chunk_index,
                chunk_size,
                config,
            )

    except Exception as e: # pylint: disable=W0718
        # Handle the exception here
        traceback.print_exc()
        print("An error occurred:", str(e))
        # You can perform additional error handling or logging as needed

    return extracted_text, extracted_blocks



