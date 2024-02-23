# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ARG parent_image
FROM $parent_image

RUN apt-get update && \
    apt install -y software-properties-common wget

RUN wget -qO- https://apt.llvm.org/llvm-snapshot.gpg.key | tee /etc/apt/trusted.gpg.d/apt.llvm.org.asc
RUN add-apt-repository 'deb http://apt.llvm.org/focal/ llvm-toolchain-focal main'

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y libstdc++-10-dev libexpat1-dev \
                       apt-utils apt-transport-https ca-certificates

RUN wget https://apt.llvm.org/llvm.sh && chmod +x llvm.sh && ./llvm.sh 14
COPY ./update_alternatives4clang.sh /
RUN /bin/bash /update_alternatives4clang.sh 14 1400

RUN apt-get install -y libc++-14-dev libc++abi-14-dev

# Download afl++
RUN git clone https://github.com/AFLplusplus/AFLplusplus.git /afl && \
    cd /afl && \
    git checkout 4124a272d821629adce648fb37ca1e7f0ce0e84f

ENV OLDPATH=$PATH
ENV PATH=/usr/bin:$PATH
ENV apt install -y libstdc++-10-dev && echo `ls /usr/lib/llvm-14` && 0
# Build without Python support as we don't need it.
# Set AFL_NO_X86 to skip flaky tests.
RUN cd /afl && unset CFLAGS && unset CXXFLAGS && export AFL_NO_X86=1 && \
    CC=/usr/bin/clang-14 CXX=/usr/bin/clang++-14 PYTHON_INCLUDE=/ make && make install && \
    make -C utils/aflpp_driver 

RUN cp /afl/utils/aflpp_driver/libAFLDriver.a / 
RUN cp -va `llvm-config --libdir`/libc++* /afl/
RUN cp -va `llvm-config --libdir`/libunwind* /afl/


RUN echo "int main(int argc, char *argv[]) { return argc - 1; }" > simple.c 
RUN /afl/afl-clang-lto simple.c

ENV PATH=$OLDPATH