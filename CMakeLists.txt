cmake_minimum_required(VERSION 3.18)
set(CMAKE_CXX_STANDARD 14)

project(craytraverse)

add_compile_definitions(VERSION_INFO="0.1.7")

add_subdirectory(src)
set(CMAKE_VERBOSE_MAKEFILE on)

install(TARGETS rtrace_c rcontrib_c LIBRARY DESTINATION craytraverse/crenderer)

if(SKBUILD)
    set(INSTALL_PATH ${SKBUILD_SCRIPTS_DIR})
else()
    set(INSTALL_PATH bin)
endif()

install(TARGETS rtrace rcontrib  total cnt rcalc getinfo vwrays
    pvalue pcompos pcomb pfilt oconv gendaylit xform RUNTIME DESTINATION ${INSTALL_PATH})

