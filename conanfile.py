#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os

class MongoCxxConan(ConanFile):
    name = "mongo-cxx-driver"
    version = "3.3.0"
    url = "https://github.com/mongodb/mongo-cxx-driver"
    homepage = "https://github.com/mongodb/mongo-cxx-driver"
    description = "C++ Driver for MongoDB"
    license = "https://github.com/mongodb/mongo-cxx-driver/blob/r{0}/LICENSE".format(version)
    settings = "os", "compiler", "arch", "build_type"
    requires = 'mongo-c-driver/1.11.0@bisect/stable'
    options = {"shared": [True, False], "fPIC": [True, False], "use_17_standard": [True, False]}
    default_options = "shared=True", "fPIC=True", "use_17_standard=False"
    exports_sources = ["CMakeLists.txt", "diff.patch"]
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    generators = "cmake"

    def source(self):
        tools.get("https://github.com/mongodb/mongo-cxx-driver/archive/r{0}.tar.gz".format(self.version))
        extracted_dir = "mongo-cxx-driver-r{0}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)
        tools.patch(base_path=self._source_subfolder, patch_file="diff.patch")

    def requirements(self):
        if not self.options.use_17_standard:
            self.requires('boost/[>1.66.0]@conan/stable')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        if self.options.use_17_standard:
            cmake.definitions["CMAKE_CXX_STANDARD"] = "17"
            cmake.definitions["BSONCXX_POLY_USE_STD"] = True
        else:
            cmake.definitions["CMAKE_CXX_STANDARD"] = "11"
            cmake.definitions["BSONCXX_POLY_USE_BOOST"] = True
            cmake.definitions["BSONCXX_POLY_USE_STD"] = False
            cmake.definitions["BSONCXX_POLY_USE_MNMLSTC"] = False

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", src=self._source_subfolder)

        # cmake installs all the files
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ['mongocxx', 'bsoncxx'] if self.options.shared else ['mongocxx-static', 'bsoncxx-static']
