#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os
import shutil


class SIPConan(ConanFile):
    name = "sip"
    version = "4.19.14"
    description = "SIP Python binding for C/C++ (Used by PyQt)"
    topics = ("conan", "python", "binding", "sip")
    url = "https://github.com/zehome/conan-sip"
    homepage = "https://www.riverbankcomputing.com/software/sip/"
    author = "Laurent Coustet <ed@zehome.com>"
    license = "GPL-3.0-only"
    generators = "txt"
    settings = "os", "compiler", "build_type", "arch"

    options = {'shared': [True, False]}
    default_options = 'shared=True'
    _source_subfolder = "sip-src"

    def source(self):
        source_url = "https://www.riverbankcomputing.com/static/Downloads/sip"
        tools.get("{0}/sip-{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version

        if os.path.exists(self._source_subfolder):
            shutil.rmtree(self._source_subfolder)
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        if self.settings.os == "Windows":
            PATH = "{0};{1}".format(self.env.get("PYTHON_DIR"), os.environ["PATH"])
        else:
            PATH = "{0}:{1}".format(os.path.join(self.env.get("PYTHON_DIR"), "bin"), os.environ["PATH"])
        with tools.chdir(self._source_subfolder):
            with tools.environment_append({"PATH": PATH}):
                self.run("python --version")
                self.run("python configure.py --sip-module={module} {static}"
                    "--bindir={bindir} --destdir={destdir} --incdir={incdir} "
                    "--sipdir={sipdir} --pyidir={pyidir}".format(
                        module="PyQt5.sip",
                        static="--static " if not self.options.shared else '',
                        bindir=os.path.join(self.build_folder, "bin"),
                        destdir=os.path.join(self.build_folder, "site-packages"),
                        incdir=os.path.join(self.build_folder, "include"),
                        sipdir=os.path.join(self.build_folder, "sip"),
                        pyidir=os.path.join(self.build_folder, "site-packages", "PyQt5"),
                    ),
                    run_environment=True)
                if self.settings.os == "Windows":
                    vcvars = tools.vcvars_command(self.settings)
                    self.run("{0} && nmake".format(vcvars))
                    self.run("{0} && nmake install".format(vcvars))
                else:
                    self.run("make", run_environment=True)
                    self.run("make install", run_environment=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE-GPL2", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE-GPL3", dst="licenses", src=self._source_subfolder)
        self.copy("*", src="bin", dst="bin")
        self.copy("*", "lib", "lib")
        self.copy("*", src="site-packages", dst="site-packages")
        self.copy("*.h", src="include", dst="include")

    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "site-packages"))
