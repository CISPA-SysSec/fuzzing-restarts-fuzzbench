FROM gcr.io/oss-fuzz-base/base-builder@sha256:87ca1e9e19235e731fac8de8d1892ebe8d55caf18e7aa131346fc582a2034fdd
ENV DEBIAN_FRONTEND=noninteractive
ENV TARGET_VERSION="2.34"
RUN echo "deb-src http://archive.ubuntu.com/ubuntu/ focal main" | tee -a /etc/apt/sources.list
RUN echo "deb-src http://archive.ubuntu.com/ubuntu/ focal-updates main" | tee -a /etc/apt/sources.list
RUN echo "deb-src http://archive.ubuntu.com/ubuntu/ focal-backports main restricted universe multiverse" | tee -a /etc/apt/sources.list
RUN git clone https://github.com/xuesu/binutils_libfuzzer.git
WORKDIR binutils_libfuzzer
RUN apt update -y && apt build-dep binutils=${TARGET_VERSION} -y
COPY build.sh $SRC/
COPY benchmark.yaml $OUT/
ADD seeds $OUT/seeds
