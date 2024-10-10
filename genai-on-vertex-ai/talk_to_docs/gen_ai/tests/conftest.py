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
import os
import pytest
from gen_ai import constants


@pytest.fixture(autouse=True, scope="session")
def override_processed_files_dir():
    """Overrides the `PROCESSED_FILES_DIR` constant for tests.

    This fixture temporarily changes the directory where processed files are stored
    during test execution. The original directory is restored after all tests are
    completed.

    Yields:
        None

    Example usage:
        This fixture is automatically applied to all tests in the session due to 
        `autouse=True`. There is no need to explicitly use it in your test functions.
    """
    original_dir = constants.PROCESSED_FILES_DIR
    constants.PROCESSED_FILES_DIR = f'{os.getenv("HOME")}/resources/dataset_name/main_folder'
    yield
    constants.PROCESSED_FILES_DIR = original_dir