import info


class subinfo(info.infoclass):
    def setTargets(self):
        self.versionInfo.setDefaultValues()

        self.description = "TNef pim library"

    def setDependencies(self):
        self.runtimeDependencies["virtual/base"] = "default"
        self.buildDependencies["kde/frameworks/extra-cmake-modules"] = "default"
        self.runtimeDependencies["libs/qt5/qtbase"] = "default"
        self.runtimeDependencies["kde/pim/kcalcore"] = "default"
        self.runtimeDependencies["kde/pim/kcontacts"] = "default"
        self.runtimeDependencies["kde/pim/kcalutils"] = "default"


from Package.CMakePackageBase import *


class Package(CMakePackageBase):
    def __init__(self):
        CMakePackageBase.__init__(self)
