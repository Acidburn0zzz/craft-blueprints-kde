# -*- coding: utf-8 -*-
import info


class subinfo(info.infoclass):
    def setTargets(self):
        self.versionInfo.setDefaultValues(packageName="clang-tools-extra", gitUrl="[git]https://git.llvm.org/git/clang-tools-extra.git")

    def setDependencies(self):
        self.runtimeDependencies["virtual/base"] = "default"
        self.runtimeDependencies["libs/llvm-meta/llvm"] = "default"


from Package.VirtualPackageBase import *


class Package(SourceComponentPackageBase):
    def __init__(self, **args):
        SourceComponentPackageBase.__init__(self)
