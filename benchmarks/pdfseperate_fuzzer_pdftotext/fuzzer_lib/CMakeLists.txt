
set(poppler_SRCS
  ../goo/gbase64.cc
  ../goo/gbasename.cc
  ../goo/gfile.cc
  ../goo/GooTimer.cc
  ../goo/GooString.cc
  ../goo/NetPBMWriter.cc
  ../goo/PNGWriter.cc
  ../goo/TiffWriter.cc
  ../goo/JpegWriter.cc
  ../goo/ImgWriter.cc
  ../goo/gstrtod.cc
  ../goo/grandom.cc
  ../goo/glibc.cc
  ../goo/glibc_strtok_r.cc
  ../fofi/FoFiBase.cc
  ../fofi/FoFiEncodings.cc
  ../fofi/FoFiTrueType.cc
  ../fofi/FoFiType1.cc
  ../fofi/FoFiType1C.cc
  ../fofi/FoFiIdentifier.cc
  ../poppler/Annot.cc
  ../poppler/Array.cc
  ../poppler/CachedFile.cc
  ../poppler/Catalog.cc
  ../poppler/CharCodeToUnicode.cc
  ../poppler/CMap.cc
  ../poppler/DateInfo.cc
  ../poppler/Decrypt.cc
  ../poppler/Dict.cc
  ../poppler/Error.cc
  ../poppler/FileSpec.cc
  ../poppler/FontEncodingTables.cc
  ../poppler/Form.cc
  ../poppler/FontInfo.cc
  ../poppler/Function.cc
  ../poppler/Gfx.cc
  ../poppler/GfxFont.cc
  ../poppler/GfxState.cc
  ../poppler/GlobalParams.cc
  ../poppler/Hints.cc
  ../poppler/JArithmeticDecoder.cc
  ../poppler/JBIG2Stream.cc
  ../poppler/Lexer.cc
  ../poppler/Link.cc
  ../poppler/Linearization.cc
  ../poppler/LocalPDFDocBuilder.cc
  ../poppler/MarkedContentOutputDev.cc
  ../poppler/NameToCharCode.cc
  ../poppler/Object.cc
  ../poppler/OptionalContent.cc
  ../poppler/Outline.cc
  ../poppler/OutputDev.cc
  ../poppler/Page.cc
  ../poppler/PageTransition.cc
  ../poppler/Parser.cc
  ../poppler/PDFDoc.cc
  ../poppler/PDFDocEncoding.cc
  ../poppler/PDFDocFactory.cc
  ../poppler/ProfileData.cc
  ../poppler/PreScanOutputDev.cc
  ../poppler/PSTokenizer.cc
  ../poppler/SignatureInfo.cc
  ../poppler/Stream.cc
  ../poppler/StructTreeRoot.cc
  ../poppler/StructElement.cc
  ../poppler/UnicodeMap.cc
  ../poppler/UnicodeMapFuncs.cc
  ../poppler/UnicodeTypeTable.cc
  ../poppler/UTF.cc
  ../poppler/XRef.cc
  ../poppler/PSOutputDev.cc
  ../poppler/TextOutputDev.cc
  ../poppler/PageLabelInfo.cc
  ../poppler/SecurityHandler.cc
  ../poppler/StdinCachedFile.cc
  ../poppler/StdinPDFDocBuilder.cc
  ../poppler/Sound.cc
  ../poppler/ViewerPreferences.cc
  ../poppler/Movie.cc
  ../poppler/Rendition.cc
  ../poppler/CertificateInfo.cc
)
set(poppler_LIBS ${FREETYPE_LIBRARIES})
if(ENABLE_SPLASH)
  set(poppler_SRCS ${poppler_SRCS}
    ../poppler/SplashOutputDev.cc
    ../splash/Splash.cc
    ../splash/SplashBitmap.cc
    ../splash/SplashClip.cc
    ../splash/SplashFTFont.cc
    ../splash/SplashFTFontEngine.cc
    ../splash/SplashFTFontFile.cc
    ../splash/SplashFont.cc
    ../splash/SplashFontEngine.cc
    ../splash/SplashFontFile.cc
    ../splash/SplashFontFileID.cc
    ../splash/SplashPath.cc
    ../splash/SplashPattern.cc
    ../splash/SplashScreen.cc
    ../splash/SplashState.cc
    ../splash/SplashXPath.cc
    ../splash/SplashXPathScanner.cc
  )
endif()
if(FONTCONFIG_FOUND)
  set(poppler_LIBS ${poppler_LIBS} ${FONTCONFIG_LIBRARIES})
endif()

if(JPEG_FOUND)
  set(poppler_SRCS ${poppler_SRCS}
    ../poppler/DCTStream.cc
  )
  set(poppler_LIBS ${poppler_LIBS} ${JPEG_LIBRARIES})
endif()
if(ENABLE_ZLIB)
  set(poppler_SRCS ${poppler_SRCS}
    ../poppler/FlateEncoder.cc
  )
  set(poppler_LIBS ${poppler_LIBS} ${ZLIB_LIBRARIES})
endif()
if(ENABLE_ZLIB_UNCOMPRESS)
  set(poppler_SRCS ${poppler_SRCS}
    ../poppler/FlateStream.cc
  )
endif()
if(ENABLE_LIBCURL)
  set(poppler_SRCS ${poppler_SRCS}
    ../poppler/CurlCachedFile.cc
    ../poppler/CurlPDFDocBuilder.cc
  )
  set(poppler_LIBS ${poppler_LIBS} ${CURL_LIBRARIES})
endif()
if (ENABLE_NSS3)
  set(poppler_SRCS ${poppler_SRCS}
    ../poppler/SignatureHandler.cc
  )
  if(${CMAKE_VERSION} VERSION_LESS "3.6.0")
    set(poppler_LIBS ${poppler_LIBS} ${NSS3_LIBRARIES})
    include_directories(SYSTEM ${NSS3_INCLUDE_DIRS})
  else()
    set(poppler_LIBS ${poppler_LIBS} PkgConfig::NSS3)
  endif()
endif()
if (OpenJPEG_FOUND)
  set(poppler_SRCS ${poppler_SRCS}
    ../poppler/JPEG2000Stream.cc
  )
  set(poppler_LIBS ${poppler_LIBS} openjp2)
else ()
  set(poppler_SRCS ${poppler_SRCS}
    ../poppler/JPXStream.cc
  )
endif()
if(USE_CMS)
  set(poppler_LIBS ${poppler_LIBS} ${LCMS2_LIBRARIES})
endif()
if(WIN32)
  # use clean APIs
  add_definitions(-DWIN32_LEAN_AND_MEAN)
  # gdi32 is needed under win32
  set(poppler_LIBS ${poppler_LIBS} gdi32)
endif()
if(PNG_FOUND)
  set(poppler_LIBS ${poppler_LIBS} ${PNG_LIBRARIES})
endif()
if(TIFF_FOUND)
  set(poppler_LIBS ${poppler_LIBS} ${TIFF_LIBRARIES})
endif()

if (GPERF AND RUN_GPERF_IF_PRESENT)
    macro(ADD_GPERF_FILE input)
        add_custom_command(OUTPUT ../poppler/${input}.c
                       COMMAND gperf ../poppler/${input}.gperf > ${CMAKE_CURRENT_BINARY_DIR}/../poppler/${input}.c
                       COMMAND gperf ../poppler/${input}.gperf > ${CMAKE_CURRENT_SOURCE_DIR}/../poppler/${input}.pregenerated.c
                       DEPENDS ../poppler/${input}.gperf
                       WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

        set(poppler_SRCS ${poppler_SRCS}
            ../poppler/${input}.c
        )
    endmacro()
else()
    macro(ADD_GPERF_FILE input)
        set(poppler_SRCS ${poppler_SRCS}
            ../poppler/${input}.pregenerated.c
        )
    endmacro()
endif()

ADD_GPERF_FILE(CourierWidths)
ADD_GPERF_FILE(CourierBoldWidths)
ADD_GPERF_FILE(CourierBoldObliqueWidths)
ADD_GPERF_FILE(CourierObliqueWidths)
ADD_GPERF_FILE(HelveticaWidths)
ADD_GPERF_FILE(HelveticaBoldWidths)
ADD_GPERF_FILE(HelveticaBoldObliqueWidths)
ADD_GPERF_FILE(HelveticaObliqueWidths)
ADD_GPERF_FILE(SymbolWidths)
ADD_GPERF_FILE(TimesBoldWidths)
ADD_GPERF_FILE(TimesBoldItalicWidths)
ADD_GPERF_FILE(TimesItalicWidths)
ADD_GPERF_FILE(TimesRomanWidths)
ADD_GPERF_FILE(ZapfDingbatsWidths)


add_library(popplerfuzzer ${poppler_SRCS})

set_source_files_properties( ${poppler_SRCS} COMPILE_FLAGS "-fsanitize=fuzzer-no-link" )
set_target_properties(popplerfuzzer PROPERTIES VERSION 97.0.0 SOVERSION 97)
set_target_properties(popplerfuzzer PROPERTIES COMPILE_FLAGS "-fsanitize=fuzzer-no-link" )
set_target_properties(popplerfuzzer PROPERTIES LINK_FLAGS  "-fsanitize=fuzzer-no-link" )
if(MINGW AND BUILD_SHARED_LIBS)
    get_target_property(POPPLER_SOVERSION popplerfuzzer SOVERSION)
endif()
target_link_libraries(popplerfuzzer LINK_PRIVATE ${poppler_LIBS})
if(CMAKE_USE_PTHREADS_INIT)
   target_link_libraries(popplerfuzzer LINK_PRIVATE Threads::Threads)
endif()
install(TARGETS popplerfuzzer RUNTIME DESTINATION bin LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

if(ENABLE_UNSTABLE_API_ABI_HEADERS)
  install(FILES
    ../poppler/Annot.h
    ../poppler/Array.h
    ../poppler/CachedFile.h
    ../poppler/Catalog.h
    ../poppler/CharCodeToUnicode.h
    ../poppler/CMap.h
    ../poppler/DateInfo.h
    ../poppler/Decrypt.h
    ../poppler/Dict.h
    ../poppler/Error.h
    ../poppler/FileSpec.h
    ../poppler/FontEncodingTables.h
    ../poppler/FontInfo.h
    ../poppler/Form.h
    ../poppler/Function.h
    ../poppler/Gfx.h
    ../poppler/GfxFont.h
    ../poppler/GfxState.h
    ../poppler/GfxState_helpers.h
    ../poppler/GlobalParams.h
    ../poppler/Hints.h
    ../poppler/JArithmeticDecoder.h
    ../poppler/JBIG2Stream.h
    ../poppler/Lexer.h
    ../poppler/Link.h
    ../poppler/Linearization.h
    ../poppler/LocalPDFDocBuilder.h
    ../poppler/MarkedContentOutputDev.h
    ../poppler/Movie.h
    ../poppler/NameToCharCode.h
    ../poppler/Object.h
    ../poppler/OptionalContent.h
    ../poppler/Outline.h
    ../poppler/OutputDev.h
    ../poppler/Page.h
    ../poppler/PageTransition.h
    ../poppler/Parser.h
    ../poppler/PDFDoc.h
    ../poppler/PDFDocBuilder.h
    ../poppler/PDFDocEncoding.h
    ../poppler/PDFDocFactory.h
    ../poppler/PopplerCache.h
    ../poppler/ProfileData.h
    ../poppler/PreScanOutputDev.h
    ../poppler/PSTokenizer.h
    ../poppler/Rendition.h
    ../poppler/CertificateInfo.h
    ../poppler/Stream-CCITT.h
    ../poppler/Stream.h
    ../poppler/StructElement.h
    ../poppler/StructTreeRoot.h
    ../poppler/UnicodeMap.h
    ../poppler/UnicodeMapFuncs.h
    ../poppler/UnicodeMapTables.h
    ../poppler/UnicodeTypeTable.h
    ../poppler/UnicodeCClassTables.h
    ../poppler/UnicodeCompTables.h
    ../poppler/UnicodeDecompTables.h
    ../poppler/ViewerPreferences.h
    ../poppler/XRef.h
    ../poppler/CharTypes.h
    ../poppler/ErrorCodes.h
    ../poppler/NameToUnicodeTable.h
    ../poppler/PSOutputDev.h
    ../poppler/TextOutputDev.h
    ../poppler/SecurityHandler.h
    ../poppler/StdinCachedFile.h
    ../poppler/StdinPDFDocBuilder.h
    ../poppler/UTF.h
    ../poppler/Sound.h
    ${CMAKE_CURRENT_BINARY_DIR}/../poppler/poppler-config.h
    DESTINATION ../include/poppler)
  install(FILES
    ../goo/GooTimer.h
    ../goo/GooString.h
    ../goo/gmem.h
    ../goo/gdir.h
    ../goo/gfile.h
    ../goo/ImgWriter.h
    ../goo/GooCheckedOps.h
    ../goo/GooLikely.h
    ../goo/gstrtod.h
    ../goo/grandom.h
    DESTINATION ../include/../poppler/goo)
  if(PNG_FOUND)
    install(FILES
      ../goo/PNGWriter.h
      DESTINATION ../include/../poppler/goo)
  endif()
  if(TIFF_FOUND)
    install(FILES
      ../goo/TiffWriter.h
      DESTINATION ../include/../poppler/goo)
  endif()
  if(JPEG_FOUND)
    install(FILES
      ../goo/JpegWriter.h
      DESTINATION ../include/../poppler/goo)
  endif()
  install(FILES
    ../fofi/FoFiBase.h
    ../fofi/FoFiEncodings.h
    ../fofi/FoFiTrueType.h
    ../fofi/FoFiType1.h
    ../fofi/FoFiType1C.h
    ../fofi/FoFiIdentifier.h
    DESTINATION ../include/../poppler/fofi)
  if(ENABLE_LIBCURL)
    install(FILES
      ../poppler/CurlCachedFile.h
      ../poppler/CurlPDFDocBuilder.h
      DESTINATION ../include/poppler)
  endif()
  if(OpenJPEG_FOUND)
    install(FILES
      ../poppler/JPEG2000Stream.h
      DESTINATION ../include/poppler)
  else()
    install(FILES
      ../poppler/JPXStream.h
      DESTINATION ../include/poppler)
  endif()
  if(ENABLE_SPLASH)
    install(FILES
      ../poppler/SplashOutputDev.h
      DESTINATION ../include/poppler)
    install(FILES
      ../splash/Splash.h
      ../splash/SplashBitmap.h
      ../splash/SplashClip.h
      ../splash/SplashErrorCodes.h
      ../splash/SplashFTFont.h
      ../splash/SplashFTFontEngine.h
      ../splash/SplashFTFontFile.h
      ../splash/SplashFont.h
      ../splash/SplashFontEngine.h
      ../splash/SplashFontFile.h
      ../splash/SplashFontFileID.h
      ../splash/SplashGlyphBitmap.h
      ../splash/SplashMath.h
      ../splash/SplashPath.h
      ../splash/SplashPattern.h
      ../splash/SplashScreen.h
      ../splash/SplashState.h
      ../splash/SplashTypes.h
      ../splash/SplashXPath.h
      ../splash/SplashXPathScanner.h
      DESTINATION ../include/../poppler/splash)
  endif()
  if(CAIRO_FOUND)
    install(FILES
      ../poppler/CairoFontEngine.h
      ../poppler/CairoOutputDev.h
      ../poppler/CairoRescaleBox.h
      DESTINATION ../include/poppler)
  endif()
endif()

