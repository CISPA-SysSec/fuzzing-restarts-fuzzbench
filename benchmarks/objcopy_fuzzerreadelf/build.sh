
if  [[ "$CFLAGS" == *"-runtime-counter-relocation"* ]]; then \
	CXXFLAGS=`echo $CXXFLAGS | sed -e 's/-mllvm//g' -e 's/-runtime-counter-relocation//g'` 
	LDFLAGS=`echo $LDFLAGS | sed -e 's/-mllvm//g' -e 's/-runtime-counter-relocation//g'` 
	export CXXFLAGS=`echo $CXXFLAGS | sed -e 's/-mllvm//g' -e 's/-runtime-counter-relocation//g'` 
	export LDFLAGS=`echo $LDFLAGS | sed -e 's/-mllvm//g' -e 's/-runtime-counter-relocation//g'` 
fi
export CFLAGS="${CFLAGS} -v -O3 -g -fPIC -ldl"
export CXXFLAGS="${CXXFLAGS} -v -O3 -g -fPIC"
export LDFLAGS="${LDFLAGS} -v -O3 -g -fPIC"
make distclean || true
make clean || true
rm -r **/config.cache || true
./configure 
make -j30
cp binutils/fuzzerreadelf $OUT
