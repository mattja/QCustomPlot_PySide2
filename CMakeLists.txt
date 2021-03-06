cmake_minimum_required(VERSION 3.12)
cmake_policy(VERSION 3.12)

project(QCustomPlot)

find_package(Qt5 REQUIRED COMPONENTS Core Gui Widgets PrintSupport)

get_target_property(QtCore_location Qt5::Core LOCATION)
get_filename_component(QtCore_libdir ${QtCore_location} DIRECTORY)
message("QtCore_location is ${QtCore_location}.")
get_target_property(QtGui_location Qt5::Gui LOCATION)
get_filename_component(QtGui_libdir ${QtGui_location} DIRECTORY)
message("QtGui_location is ${QtGui_location}.")
get_target_property(QtWidgets_location Qt5::Widgets LOCATION)
get_filename_component(QtWidgets_libdir ${QtWidgets_location} DIRECTORY)
message("QtWidgets_location is ${QtWidgets_location}.")
get_target_property(QtPrintSupport_location Qt5::PrintSupport LOCATION)
get_filename_component(QtPrintSupport_libdir ${QtPrintSupport_location} DIRECTORY)
message("QtPrintSupport_location is ${QtPrintSupport_location}.")

set(CMAKE_AUTOMOC ON)

set(CMAKE_CXX_STANDARD 11)
set(sample_library "qcustomplot")
set(bindings_library "QCustomPlot")
set(wrapped_header ${CMAKE_SOURCE_DIR}/bindings.h)
set(typesystem_file ${CMAKE_SOURCE_DIR}/bindings.xml)

set(generated_sources
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcustomplot_module_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcp_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcpaxisrect_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcpaxis_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcpbars_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcpcolormap_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcpcolorscale_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcpgraph_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcplayerable_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcplayer_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcplayoutelement_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcplayoutgrid_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcplayout_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcplegend_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcppainter_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcpselectionrect_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qcustomplot_wrapper.cpp)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)

if(NOT python_interpreter)
    find_program(python_interpreter "python")
endif()

set(PYSIDE2_DIR ${Python3_SITELIB}/PySide2)

macro(pyside2_config option output_var)
    if(${ARGC} GREATER 2)
        set(is_list ${ARGV2})
    else()
        set(is_list "")
    endif()

    execute_process(
      COMMAND ${python_interpreter} "${PYSIDE2_DIR}/examples/utils/pyside2_config.py"
		${option}
      OUTPUT_VARIABLE ${output_var}
      OUTPUT_STRIP_TRAILING_WHITESPACE)

    if ("${${output_var}}" STREQUAL "")
        message(FATAL_ERROR "Error: Calling pyside2_config.py ${option} returned no output.")
    endif()
    if(is_list)
        string (REPLACE " " ";" ${output_var} "${${output_var}}")
    endif()
endmacro()

pyside2_config(--shiboken2-module-path shiboken2_module_path)
pyside2_config(--shiboken2-generator-path shiboken2_generator_path)
pyside2_config(--python-include-path python_include_dir)
pyside2_config(--shiboken2-generator-include-path shiboken_include_dir 1)
pyside2_config(--shiboken2-module-shared-libraries-cmake shiboken_shared_libraries 0)
pyside2_config(--pyside2-shared-libraries-cmake pyside2_link 0)

set(shiboken_path "${shiboken2_generator_path}/shiboken2${CMAKE_EXECUTABLE_SUFFIX}")
if(NOT EXISTS ${shiboken_path})
    message(FATAL_ERROR "Shiboken executable not found at path: ${shiboken_path}")
endif()

set(CMAKE_SKIP_BUILD_RPATH FALSE)
set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)
set(CMAKE_INSTALL_RPATH ${shiboken2_module_path} ${CMAKE_CURRENT_SOURCE_DIR} ${QtCore_libdir} ${QtGui_libdir} ${QtWidgets_libdir} ${QtPrintSupport_libdir})
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

set(${sample_library}_sources qcustomplot.cpp)
add_library(${sample_library} SHARED ${${sample_library}_sources})
target_link_libraries(${sample_library} Qt5::Core Qt5::Gui Qt5::Widgets Qt5::PrintSupport)
set_property(TARGET ${sample_library} PROPERTY PREFIX "")

get_target_property(qtcore_lib_includes Qt5::Core INTERFACE_INCLUDE_DIRECTORIES)
get_target_property(qtgui_lib_includes Qt5::Gui INTERFACE_INCLUDE_DIRECTORIES)
get_target_property(qtwidgets_lib_includes Qt5::Widgets INTERFACE_INCLUDE_DIRECTORIES)
get_target_property(qtprintsupport_lib_includes Qt5::PrintSupport INTERFACE_INCLUDE_DIRECTORIES)
set(all_lib_includes "${qtcore_lib_includes};${qtgui_lib_includes};${qtwidgets_lib_includes};${qtprintsupport_lib_includes}")
list(JOIN all_lib_includes ";-I" lib_includes)
set(lib_includes "-I${lib_includes}")

target_compile_definitions(${sample_library} PRIVATE BINDINGS_BUILD)


set(shiboken_options --generator-set=shiboken --enable-parent-ctor-heuristic
    --enable-return-value-heuristic --use-isnull-as-nb_nonzero
    --avoid-protected-hack
    --enable-pyside-extensions
    ${lib_includes}
    -I${CMAKE_SOURCE_DIR}
    -T${CMAKE_SOURCE_DIR}
    -T${PYSIDE2_DIR}/typesystems/
    --output-directory=${CMAKE_CURRENT_BINARY_DIR}
    )

set(generated_sources_dependencies ${wrapped_header} ${typesystem_file})

add_custom_command(OUTPUT ${generated_sources}
                    COMMAND ${shiboken_path}
                    ${shiboken_options} ${wrapped_header} ${typesystem_file}
                    DEPENDS ${generated_sources_dependencies}
                    IMPLICIT_DEPENDS CXX ${wrapped_header}
                    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
                    COMMENT "Running generator for ${typesystem_file}.")

set(${bindings_library}_sources ${generated_sources})

add_library(${bindings_library} MODULE ${${bindings_library}_sources})

target_include_directories(${bindings_library} PRIVATE ${python_include_dir})
target_include_directories(${bindings_library} PRIVATE ${PYSIDE2_DIR}/include/)
target_include_directories(${bindings_library} PRIVATE ${PYSIDE2_DIR}/include/QtCore)
target_include_directories(${bindings_library} PRIVATE ${PYSIDE2_DIR}/include/QtGui)
target_include_directories(${bindings_library} PRIVATE ${PYSIDE2_DIR}/include/QtWidgets)
target_include_directories(${bindings_library} PRIVATE ${PYSIDE2_DIR}/include/QtPrintSupport)
target_include_directories(${bindings_library} PRIVATE ${shiboken_include_dir})
target_include_directories(${bindings_library} PRIVATE ${CMAKE_SOURCE_DIR})

target_link_libraries(${bindings_library} PRIVATE ${sample_library})
target_link_libraries(${bindings_library} PRIVATE ${shiboken_shared_libraries})
target_link_libraries(${bindings_library} PRIVATE ${pyside2_link})

set_property(TARGET ${bindings_library} PROPERTY PREFIX "")
set_property(TARGET ${bindings_library} PROPERTY OUTPUT_NAME
             "${bindings_library}${PYTHON_EXTENSION_SUFFIX}")

install(TARGETS ${bindings_library} ${sample_library}
        LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}
        RUNTIME DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}
        )
