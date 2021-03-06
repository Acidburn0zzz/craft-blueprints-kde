# -*- coding: utf-8 -*-
import info
from Package.MSBuildPackageBase import *
from Package.AutoToolsPackageBase import *


class subinfo(info.infoclass):
    def setTargets(self):
        for ver in ['0.19.8.1']:
            self.targets[ver] = 'http://ftp.gnu.org/pub/gnu/gettext/gettext-%s.tar.gz' % ver
            self.targetInstSrc[ver] = "gettext-%s" % ver
        self.patchLevel['0.19.8.1'] = 1
        self.targetDigests['0.19.8.1'] = (['ff942af0e438ced4a8b0ea4b0b6e0d6d657157c5e2364de57baa279c1c125c43'], CraftHash.HashAlgorithm.SHA256)

        #patch based on https://github.com/fanc999/gtk-msvc-projects/tree/master/gettext/0.19.8.1
        self.patchToApply['0.19.8.1'] = [("gettext-0.19.8.1-gtk-msvc-projects.diff", 1)]
        self.patchToApply['0.19.8.1'] += [("0001-gettext-tools-gnulib-lib-xalloc.h-Fix-function-signa.patch", 1)]
        self.patchToApply['0.19.8.1'] += [("0001-gettext-tools-src-Fix-linking.patch", 1)]
        self.patchToApply['0.19.8.1'] += [("0001-gettext-tools-src-x-lua.c-Fix-on-pre-C99.patch", 1)]
        self.patchToApply['0.19.8.1'] += [("0001-ostream.h-styled-ostream.h-Fix-linking.patch", 1)]
        self.patchToApply['0.19.8.1'] += [("0001-printf-parse.c-Fix-build-on-Visual-Studio-2008.patch", 1)]
        self.patchToApply['0.19.8.1'] += [("0001-tools-Fix-gnulib-lib-uniname-uniname.c-on-pre-C99.patch", 1)]
        if OsUtils.isMac():
            self.patchToApply['0.19.8.1'] += [("0001-moopp-sed-extended-regexp.patch", 1)]

        self.description = "GNU internationalization (i18n)"
        self.defaultTarget = '0.19.8.1'

    def setDependencies(self):
        self.runtimeDependencies["virtual/base"] = "default"
        self.runtimeDependencies["libs/iconv"] = "default"
        if CraftCore.compiler.isGCCLike():
            self.buildDependencies["dev-utils/msys"] = "default"


class PackageMinGW(AutoToolsPackageBase):
    def __init__(self, **args):
        AutoToolsPackageBase.__init__(self)
        self.subinfo.options.configure.args += " --disable-static --enable-shared --disable-java --disable-native-java --enable-nls --enable-c++ --with-included-gettext --with-included-glib --with-included-regex --with-gettext-tools"

class PackageMSVC(MSBuildPackageBase):
    def __init__(self, **args):
        MSBuildPackageBase.__init__(self)
        self.gettextBuildDir = os.path.join(self.sourceDir(), "win32", "vs15")
        self.subinfo.options.configure.args = "/p:UseEnv=true"
        self.subinfo.options.configure.projectFile = os.path.join(self.gettextBuildDir, "gettext.sln")


    def make(self):
        with utils.ScopedEnv({
            "LIB" : f"{os.environ['LIB']};{os.path.join(CraftStandardDirs.craftRoot() , 'lib')}",
            "INCLUDE" : f"{os.environ['INCLUDE']};{os.path.join(CraftStandardDirs.craftRoot() , 'include')}"}):
            return MSBuildPackageBase.make(self)

    def install(self):
        if not MSBuildPackageBase.install(self, installHeaders=False,
                                          buildDirs=[self.gettextBuildDir]):
            return True
        return (utils.copyFile(os.path.join(self.sourceDir(), "gettext-runtime", "intl", "msvc", "libintl.h"),
                               os.path.join(self.installDir(), "include", "libintl.h")) and
                utils.copyFile(os.path.join(self.sourceDir(), "gettext-runtime", "libasprintf", "msvc", "autosprintf.h"),
                               os.path.join(self.installDir(), "include", "autosprintf.h")))

if CraftCore.compiler.isGCCLike():
    class Package(PackageMinGW):
        def __init__(self):
            PackageMinGW.__init__(self)
else:
    class Package(PackageMSVC):
        def __init__(self):
            PackageMSVC.__init__(self)
