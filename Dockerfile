FROM python:3.7.4-slim-stretch

RUN apt-get update \
    && apt-get -y install curl build-essential libssl-dev \
    && apt-get clean \
    && pip install --upgrade pip

# Prepare environment
RUN mkdir /earthzetaorg
WORKDIR /earthzetaorg

# Install TA-lib
COPY build_helpers/* /tmp/
RUN cd /tmp && /tmp/install_ta-lib.sh && rm -r /tmp/*ta-lib*

ENV LD_LIBRARY_PATH /usr/local/lib

# Install dependencies
COPY requirements.txt requirements-common.txt /earthzetaorg/
RUN pip install numpy --no-cache-dir \
  && pip install -r requirements.txt --no-cache-dir

# Install and execute
COPY . /earthzetaorg/
RUN pip install -e . --no-cache-dir
ENTRYPOINT ["earthzetaorg"]
