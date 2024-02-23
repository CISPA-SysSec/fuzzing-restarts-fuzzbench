
set(common_srcs
  ../utils/parseargs.cc
  ../utils/Win32Console.cc
)
set(common_libs
  popplerfuzzer
)

# fuzzer_pdftotext
set(fuzzer_pdftotext_SOURCES ${common_srcs}
  fuzzer.cc ../utils/printencodings.cc
)


include_directories(
  ${CMAKE_CURRENT_SOURCE_DIR}
  ${CMAKE_CURRENT_SOURCE_DIR}/../utils
  ${CMAKE_CURRENT_BINARY_DIR}
  SYSTEM
  ${CAIRO_INCLUDE_DIRS}
)
set_source_files_properties( ${fuzzer_pdftotext_SOURCES} COMPILE_FLAGS "-fsanitize=fuzzer" )
add_executable(fuzzer_pdftotext ${fuzzer_pdftotext_SOURCES})
set_target_properties(fuzzer_pdftotext PROPERTIES COMPILE_FLAGS "-fsanitize=fuzzer" )
set_target_properties(fuzzer_pdftotext PROPERTIES LINK_FLAGS  "-fsanitize=fuzzer" )
target_link_libraries(fuzzer_pdftotext ${common_libs})
install(TARGETS fuzzer_pdftotext DESTINATION bin)
