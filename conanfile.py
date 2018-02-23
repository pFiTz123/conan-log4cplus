#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os


class Log4cplusConan(ConanFile):
    name = "log4cplus"
    version = "1.2.1"
    description = "simple to use C++ logging API, modelled after the Java log4j API"
    url = "https://github.com/bincrafters/conan-log4cplus"
    license = "BSD 2-clause, Apache-2.0"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    settings = "os", "compiler", "build_type", "arch"
    
    options = {
        "shared": [True, False], 
        "fPIC": [True, False],
        "build_loggingserver" : [True, False],
        "single_threaded" : [True, False],
        "with_iconv" : [True, False],
        "qt4_debug_appender" : [True, False],
        "qt5_debug_appender" : [True, False],
        "working_c_locale" : [True, False],
        "decorated_name" : [True, False]
    }

    default_options = (
        "shared=False", 
        "fPIC=True",
        "build_loggingserver=True",
        "single_threaded=False",
        "with_iconv=False",
        "qt4_debug_appender=False",
        "qt5_debug_appender=False",
        "working_c_locale=False",
        "decorated_name=False",
    )
    
    short_paths = True

    def configure(self):
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC
            self.options.working_c_locale = True
        else:
            self.options.working_c_locale = False
        
    def config_options(self):
        if self.options.with_iconv == True:
            raise ConanException('with_iconv option not currenltly supported')
            # This seems to be for winiconv/windows not libiconv/mac
            # If so, we need to refurbish lasotes winiconv pakage to support this options
            #self.requires("iconv/0.0.0@bincrafters/stable")

    def source(self):
        source_url = "https://downloads.sourceforge.net/project/log4cplus/log4cplus-stable"
        archive_name = self.name + "-" + self.version
        tools.get("{0}/1.2.1/{1}.zip".format(source_url, archive_name))
        os.rename(archive_name, self.source_subfolder)
        
    def build(self):
        cmake = CMake(self)
        if self.settings.compiler in ("clang", "gcc"):
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
            
        cmake.configure(build_dir=self.build_subfolder)
        cmake.definitions['LOG4CPLUS_SINGLE_THREADED'] = self.options.single_threaded
        cmake.definitions['LOG4CPLUS_BUILD_LOGGINGSERVER'] = self.options.build_loggingserver
        cmake.definitions['WITH_ICONV'] = self.options.with_iconv
        cmake.definitions['LOG4CPLUS_QT4'] = self.options.qt4_debug_appender
        cmake.definitions['LOG4CPLUS_QT5'] = self.options.qt5_debug_appender
        cmake.definitions['LOG4CPLUS_WORKING_LOCALE_DEFAULT'] = self.options.working_c_locale
        cmake.definitions["LOG4CPLUS_ENABLE_DECORATED_LIBRARY_NAME"] = self.options.decorated_name
        cmake.definitions['LOG4CPLUS_BUILD_TESTING'] = 'False'
        cmake.definitions['WITH_UNIT_TESTS'] = 'False'
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        
        if self.settings.compiler in ("clang", "gcc"):
            self.cpp_info.libs.extend(["dl", "pthread"])

        if self.settings.compiler == "Visual Studio":
            self.cpp_info.libs.append('Ws2_32')
