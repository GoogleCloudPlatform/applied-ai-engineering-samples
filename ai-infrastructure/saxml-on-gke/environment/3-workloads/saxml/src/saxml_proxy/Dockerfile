FROM python:3.10

ENV SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL True

RUN set -e

RUN apt -y update && apt install -y \
    apt-transport-https \
    curl \
    gnupg patch python3-pip

RUN curl https://bazel.build/bazel-release.pub.gpg | apt-key --keyring /usr/share/keyrings/bazel-archive-keyring.gpg add -
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/bazel-archive-keyring.gpg] https://storage.googleapis.com/bazel-apt stable jdk1.8" | tee /etc/apt/sources.list.d/bazel.list
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN apt -y update && apt install -y bazel-5.4.0 google-cloud-cli
RUN update-alternatives --install /usr/bin/bazel bazel /usr/bin/bazel-5.4.0 20

RUN pip3 install -U pip 
RUN pip3 install --upgrade numpy google-api-python-client 
RUN git clone https://github.com/google/saxml.git && \
    cd saxml && \
    git checkout r1.1.0 

WORKDIR /saxml
RUN bazel build saxml/client/python:sax.cc --compile_one_dependency
ENV PYTHONPATH "${PYTHONPATH}:/saxml/bazel-bin/saxml/client/python"


WORKDIR /app
COPY ./requirements.txt ./
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY ./ ./

CMD ["uvicorn", "sax_http_proxy_server:app", "--host", "0.0.0.0", "--port", "8080"]