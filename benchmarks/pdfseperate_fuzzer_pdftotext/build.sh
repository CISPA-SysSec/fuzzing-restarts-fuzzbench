mkdir install
mkdir build
cd build
cmake ..
cmake --build . --target fuzzer_pdftotext -j30
rm -r ../install || true
mkdir ../install  
cp fuzzer_lib/*.so* ../install
cp fuzzer/fuzzer_pdftotext ../install
cp /lib/x86_64-linux-gnu/libfreetype.so*  ../install 
cp /lib/x86_64-linux-gnu/libfontconfig.so* ../install 
cp /lib/x86_64-linux-gnu/libjpeg.so* ../install 
cp /lib/x86_64-linux-gnu/libopenjp2.so* ../install 
cp /lib/x86_64-linux-gnu/liblcms2.so* ../install 
cp /lib/x86_64-linux-gnu/libpng16.so* ../install 
cp /lib/x86_64-linux-gnu/libtiff.so* ../install 
cp /lib/x86_64-linux-gnu/libnss3.so*  ../install 
cp /lib/x86_64-linux-gnu/libnssutil3* ../install 
cp /lib/x86_64-linux-gnu/libsmime3.so*  ../install 
cp /lib/x86_64-linux-gnu/libssl3.so*  ../install 
cp /lib/x86_64-linux-gnu/libplds4.so*  ../install 
cp /lib/x86_64-linux-gnu/libplc4.so*  ../install 
cp /lib/x86_64-linux-gnu/libnspr4.so*  ../install 
cp /lib/x86_64-linux-gnu/libwebp.so* ../install 
cp /lib/x86_64-linux-gnu/libjbig.so* ../install 
cp /lib/x86_64-linux-gnu/libexpat.so*  ../install 
cp /lib/x86_64-linux-gnu/libuuid.so*  ../install 
cp /lib/x86_64-linux-gnu/libzstd.so* ../install 
cp /lib/x86_64-linux-gnu/liblzma.so* ../install 
cp ../install/* $OUT
