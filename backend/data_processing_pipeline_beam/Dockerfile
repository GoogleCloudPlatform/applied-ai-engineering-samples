# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM gcr.io/dataflow-templates-base/python311-template-launcher-base:latest AS template_launcher
FROM apache/beam_python3.11_sdk:2.57.0

COPY --from=template_launcher /opt/google/dataflow/python_template_launcher /opt/google/dataflow/python_template_launcher

# Set the working directory
ARG WORKDIR=/template
RUN mkdir -p ${WORKDIR}
RUN mkdir -p ${WORKDIR}/custom_transforms
WORKDIR ${WORKDIR}

ENV FLEX_TEMPLATE_PYTHON_SETUP_FILE="${WORKDIR}/setup.py"
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="${WORKDIR}/main.py"
ENV FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE="${WORKDIR}/requirements.txt"

# Copy the necessary files
COPY __init__.py ${WORKDIR}/__init__.py
COPY requirements.txt .
COPY setup.py .
COPY main.py .
COPY custom_transforms ${WORKDIR}/custom_transforms

# List contents for verification
RUN echo '----- listing workdir'
RUN ls -la ${WORKDIR}
RUN echo '-- listing custom_transforms--'
RUN ls -la ${WORKDIR}/custom_transforms

# Set PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:${WORKDIR}"

# Install dependencies
RUN apt-get update \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r $FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE \
    && pip download --no-cache-dir --dest /tmp/dataflow-requirements-cache -r $FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE

    # Install local package and its requirements.
RUN pip install -e "${WORKDIR}"
ENTRYPOINT ["/opt/google/dataflow/python_template_launcher"]