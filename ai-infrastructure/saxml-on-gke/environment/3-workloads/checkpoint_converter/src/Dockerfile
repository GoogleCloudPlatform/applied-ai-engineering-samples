          # Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


FROM python:3.10

ARG CLOUD_SDK_VERSION=google-cloud-cli-453.0.0-linux-x86_64.tar.gz
ARG PAXML_VERSION=1.2.0
ARG JAX_VERSION=0.4.18
ARG JAXLIB_VERSION=0.4.18
ARG ORBAX_CHECKPOINT_VERSION=0.4.8


RUN pip3 install accelerate torch transformers 
RUN pip3 install  jax==${JAX_VERSION} jaxlib==${JAXLIB_VERSION}  paxml==${PAXML_VERSION} 
RUN pip3 install -U orbax-checkpoint==${ORBAX_CHECKPOINT_VERSION}

RUN curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/${CLOUD_SDK_VERSION} && tar -xf ${CLOUD_SDK_VERSION} && ./google-cloud-sdk/install.sh
#RUN pip install git+https://github.com/google/paxml.git@main
#RUN pip install git+https://github.com/google-deepmind/chex@main

RUN git clone  https://github.com/google/saxml
WORKDIR saxml/saxml/tools

ENV PATH="${PATH}:/google-cloud-sdk/bin"

ENTRYPOINT ["/bin/bash"]