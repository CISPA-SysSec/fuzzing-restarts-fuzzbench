#!/bin/bash -eu
# Copyright 2019 Google Inc.
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
#
################################################################################

# build project
if [ "$SANITIZER" = undefined ]; then
    export CFLAGS="$CFLAGS -fno-sanitize=unsigned-integer-overflow"
    export CXXFLAGS="$CXXFLAGS -fno-sanitize=unsigned-integer-overflow"
fi
cd binutils-gdb

# Comment out the lines of logging to stderror from elfcomm.c
# This is to make it nicer to read the output of libfuzzer.
cd binutils
sed -i 's/vfprintf (stderr/\/\//' elfcomm.c
sed -i 's/fprintf (stderr/\/\//' elfcomm.c
cd ../

./configure --disable-gdb --disable-gdbserver --disable-gdbsupport \
	    --disable-libdecnumber --disable-readline --disable-sim \
	    --disable-libbacktrace --disable-gas --disable-ld --disable-werror \
      --enable-targets=all
make clean
make MAKEINFO=true && true


# Make fuzzer directory
mkdir fuzz
cp ../fuzz_*.c fuzz/
cd fuzz

LIBS="../opcodes/libopcodes.a ../libctf/.libs/libctf.a ../bfd/.libs/libbfd.a ../zlib/libz.a ../libsframe/.libs/libsframe.a ../libiberty/libiberty.a"


# Now compile the src/binutils fuzzers
cd ../binutils

# Compile the fuzzers.
# The general strategy is to remove main functions such that the fuzzer (which has its own main)
# can link against the code.

#
# Patching
#
# First do readelf. We do this by changing readelf.c to readelf.h - the others will be changed
# to fuzz_readelf.h where readelf is their respective name. The reason it's different for readelf
# is because readelf does not have a header file so we can use readelf.h instead, and changing it
# might cause an annoyance on monorail since bugs will be relocated as the files will be different.
cp ../../fuzz_*.c .
sed 's/main (int argc/old_main (int argc, char **argv);\nint old_main (int argc/' readelf.c >> readelf.h

# Patch the rest
for i in objdump nm; do
    sed -i 's/strip_main/strip_mian/g' $i.c
    sed -i 's/copy_main/copy_mian/g' $i.c
    sed 's/main (int argc/old_main32 (int argc, char **argv);\nint old_main32 (int argc/' $i.c > fuzz_$i.h
    sed -i 's/copy_mian/copy_main/g' fuzz_$i.h
done

#
# Compile fuzzers
#
fuzz_compile () {
  src=$1
  dst=$2
  extraflags=$3
  $CC $CFLAGS ${extraflags} -DHAVE_CONFIG_H -DOBJDUMP_PRIVATE_VECTORS="" -I. -I../bfd -I./../bfd -I./../include \
    -I./../zlib -DLOCALEDIR="\"/usr/local/share/locale\"" \
    -Dbin_dummy_emulation=bin_vanilla_emulation -W -Wall -MT \
    fuzz_$dst.o -MD -MP -c -o fuzz_$dst.o fuzz_$src.c
}
for i in objdump readelf nm; do
  fuzz_compile $i $i ""
done

# Fuzzers that need additional flags
fuzz_compile objdump objdump_safe "-DOBJDUMP_SAFE"
fuzz_compile readelf readelf_pef "-DREADELF_TARGETED=\"pef\""
fuzz_compile readelf readelf_elf32_bigarm "-DREADELF_TARGETED=\"elf32-bigarm\""
fuzz_compile readelf readelf_elf32_littlearm "-DREADELF_TARGETED=\"elf32-littlearm\""
fuzz_compile readelf readelf_elf64_mmix "-DREADELF_TARGETED=\"elf64-mmix\""
fuzz_compile readelf readelf_elf32_csky "-DREADELF_TARGETED=\"elf32-csky\""

#
# Link fuzzers
#
# Link the files, but only if everything went well, which we verify by checking
# the presence of some object files.
LINK_LIBS="-Wl,--start-group ${LIBS} -Wl,--end-group"
OBJ1="bucomm.o version.o filemode.o"
OBJ2="version.o unwind-ia64.o dwarf.o elfcomm.o demanguse.o"
OBJ3="dwarf.o prdbg.o rddbg.o unwind-ia64.o debug.o stabs.o rdcoff.o bucomm.o version.o filemode.o elfcomm.o od-xcoff.o demanguse.o"

declare -A fl
fl["readelf"]=${OBJ2}
fl["readelf_pef"]=${OBJ2}
fl["readelf_elf32_bigarm"]=${OBJ2}
fl["readelf_elf32_littlearm"]=${OBJ2}
fl["readelf_elf64_mmix"]=${OBJ2}
fl["readelf_elf32_csky"]=${OBJ2}
fl["objdump"]=${OBJ3}
fl["objdump_safe"]=${OBJ3}
fl["nm"]="${OBJ1} demanguse.o"
for fuzzer in ${!fl[@]}; do
  $CXX $CXXFLAGS $LIB_FUZZING_ENGINE -W -Wall -I./../zlib \
    -o $OUT/fuzz_${fuzzer} fuzz_${fuzzer}.o \
    ${fl[${fuzzer}]} ${LINK_LIBS}
done


# Copy seeds out
for fuzzname in readelf_pef readelf_elf32_csky readelf_elf64_mmix readelf_elf32_littlearm readelf_elf32_bigarm objdump objdump_safe nm; do
  cp $SRC/binary-samples/oss-fuzz-binutils/general_seeds.zip $OUT/fuzz_${fuzzname}_seed_corpus.zip
done

# Copy options files
for ft in readelf readelf_pef readelf_elf32_csky readelf_elf64_mmix readelf_elf32_littlearm readelf_elf32_bigarm objdumpnm as; do
  echo "[libfuzzer]" > $OUT/fuzz_${ft}.options
  echo "detect_leaks=0" >> $OUT/fuzz_${ft}.options
done
