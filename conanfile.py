#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil
import re

class MongoCxxConan(ConanFile):
    name = "mongo-cxx-driver"
    version = "3.3.0"
    url = "http://github.com/bincrafters/conan-mongo-cxx-driver"
    description = "C++ Driver for MongoDB"
    license = "https://github.com/mongodb/mongo-cxx-driver/blob/{0}/LICENSE".format(version)
    settings =  "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    requires = ("mongo-c-driver/1.11.0@bincrafters/stable",
        "boost_system/1.67.0@bincrafters/stable",
        "boost_utility/1.67.0@bincrafters/stable",
        "boost_smart_ptr/1.67.0@bincrafters/stable",
        "boost_optional/1.67.0@bincrafters/stable")
    generators = "cmake"

    def source(self):
        tools.get("https://github.com/mongodb/mongo-cxx-driver/archive/r{0}.tar.gz".format(self.version))
        extracted_dir = "mongo-cxx-driver-r{0}".format(self.version)
        os.rename(extracted_dir, "sources")

    def build(self):
        conan_magic_lines='''project(MONGO_CXX_DRIVER LANGUAGES CXX)
        include(../conanbuildinfo.cmake)
        conan_basic_setup()
        '''
        if self.settings.compiler == 'Visual Studio':
                conan_magic_lines += "add_definitions(-D_ENABLE_EXTENDED_ALIGNED_STORAGE)"
        
        cmake_file = "sources/CMakeLists.txt"
        tools.replace_in_file(cmake_file, "project(MONGO_CXX_DRIVER LANGUAGES CXX)", conan_magic_lines)
        content = tools.load(cmake_file)

        cmake = CMake(self)
        cmake.definitions["BSONCXX_POLY_USE_BOOST"] = 1
        cmake.configure(source_dir="sources")
        cmake.build()

    def purge(self, dir, pattern):
        for f in os.listdir(dir):
            if re.search(pattern, f):
                # print "removing {0}".format(os.path.join(dir, f))
                os.remove(os.path.join(dir, f))

    def package(self):
        self.copy(pattern="COPYING*", src="sources")
        self.copy(pattern="*.hpp", dst="include/bsoncxx", src="sources/src/bsoncxx", keep_path=True)
        self.copy(pattern="*.hpp", dst="include/mongocxx", src="sources/src/mongocxx", keep_path=True)
        self.copy(pattern="*.hpp", dst="include/bsoncxx", src="src/bsoncxx", keep_path=True)
        self.copy(pattern="*.hpp", dst="include/mongocxx", src="src/mongocxx", keep_path=True)
        # self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)

        # self.purge("lib", "lib.*testing.*".format(self.version))
        # self.purge("lib", "lib.*mocked.*".format(self.version))
        # # self.purge("lib", "lib.*_noabi.*".format(self.version))

        try:
            os.rename("lib/libmongocxx-static.a", "lib/libmongocxx.a")
        except:
            pass
        try:
            os.rename("lib/libbsoncxx-static.a", "lib/libbsoncxx.a")
        except:
            pass
        try:
            os.rename("lib/libmongocxx-static.lib", "lib/libmongocxx.lib")
        except:
            pass
        try:
            os.rename("lib/libbsoncxx-static.lib", "lib/libbsoncxx.lib")
        except:
            pass
        try:
            os.rename("lib/mongocxx-static.lib", "lib/mongocxx.lib")
        except:
            pass
        try:
            os.rename("lib/bsoncxx-static.lib", "lib/bsoncxx.lib")
        except:
            pass
        self.copy(pattern="*cxx.lib", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="lib*cxx.a", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="lib*cxx.so*", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="lib*cxx.dylib", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="lib*cxx._noabi.dylib", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['mongocxx', 'bsoncxx']


