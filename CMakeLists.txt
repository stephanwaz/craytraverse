cmake_minimum_required(VERSION 3.18)
set(CMAKE_CXX_STANDARD 14)
project(craytraverse)

add_compile_definitions(VERSION_INFO="0.1.6")

add_subdirectory(src)
set(CMAKE_VERBOSE_MAKEFILE on)

install(TARGETS rtrace_c rcontrib_c LIBRARY DESTINATION craytraverse/crenderer)
install(TARGETS craytraverse LIBRARY DESTINATION craytraverse)
install(TARGETS rtrace rcontrib  total cnt rcalc getinfo vwrays
    pvalue pcompos pcomb pfilt oconv gendaylit xform RUNTIME DESTINATION bin)

