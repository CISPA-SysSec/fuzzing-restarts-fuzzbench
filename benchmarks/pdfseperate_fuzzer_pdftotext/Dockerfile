FROM gcr.io/oss-fuzz-base/base-builder@sha256:87ca1e9e19235e731fac8de8d1892ebe8d55caf18e7aa131346fc582a2034fdd
ENV DEBIAN_FRONTEND=noninteractive
ENV TARGET_VERSION="0.86.1"
RUN echo "deb-src http://archive.ubuntu.com/ubuntu/ focal main" | tee -a /etc/apt/sources.list
RUN echo "deb-src http://archive.ubuntu.com/ubuntu/ focal-updates main" | tee -a /etc/apt/sources.list
RUN echo "deb-src http://archive.ubuntu.com/ubuntu/ focal-backports main restricted universe multiverse" | tee -a /etc/apt/sources.list
RUN git clone https://gitlab.freedesktop.org/poppler/poppler.git
WORKDIR poppler
RUN git fetch --all --tags
RUN git checkout tags/poppler-${TARGET_VERSION} -b sileo_targets
RUN apt update -y && apt build-dep poppler-utils=${TARGET_VERSION} -y
COPY build.sh $SRC/
COPY benchmark.yaml $OUT/
ADD seeds $OUT/seeds
COPY mygitpatch $SRC/poppler
RUN git apply $SRC/poppler/mygitpatch
ADD fuzzer $SRC/poppler/fuzzer
ADD fuzzer_lib $SRC/poppler/fuzzer_lib
