import info
from CraftOS.osutils import OsUtils


class subinfo(info.infoclass):
    def setTargets(self):
        self.svnTargets['master'] = 'git://anongit.kde.org/rkward'
        self.defaultTarget = 'master'

    def setDependencies(self):
        self.runtimeDependencies["binary/r-base"] = "default"
        self.runtimeDependencies["kde/frameworks/tier1/ki18n"] = "default"
        self.runtimeDependencies["kde/frameworks/tier3/ktexteditor"] = "default"
        self.runtimeDependencies["kde/frameworks/tier1/kwindowsystem"] = "default"
        self.runtimeDependencies["kde/frameworks/tier3/kdewebkit"] = "default"
        # not strictly runtimeDependencies, but should be included in the package
        self.runtimeDependencies["kde/applications/kate"] = "default"
        self.runtimeDependencies["kde/frameworks/tier1/breeze-icons"] = "default"


from Source.GitSource import *


class RKTranslations(GitSource):
    def __init__(self, rkwardPackage):
        GitSource.__init__(self)
        self.rkwardPackage = rkwardPackage

    def repositoryUrl(self):
        return "git://anongit.kde.org/scratch/tfry/rkward-po-export"

    def checkoutDir(self):
        """ clone _into_ the RKWard source tree """
        return os.path.join(self.rkwardPackage.checkoutDir(), "i18n", "po")

    def sourceDir(self):
        return self.checkoutDir(self)


from Package.CMakePackageBase import *


class Package(CMakePackageBase):
    def __init__(self):
        CMakePackageBase.__init__(self)

        if OsUtils.isWin():
            if CraftCore.compiler.isX64():
                self.r_dir = os.path.join(CraftCore.standardDirs.craftRoot(), "lib", "R", "bin", "x64")
            else:
                self.r_dir = os.path.join(CraftCore.standardDirs.craftRoot(), "lib", "R", "bin", "i386")
            self.subinfo.options.configure.args = " -DR_EXECUTABLE=" + os.path.join(self.r_dir, "R.exe").replace("\\\\",
                                                                                                                 "/")
            if CraftCore.compiler.isMSVC():
                self.realconfigure = self.configure
                self.configure = self.msvcconfigure
                # NOTE: On Mac, we'll let RKWard try to auto-detect R (installed with officlal installer, or MacPorts, or something else)
        elif OsUtils.isMac():
            self.subinfo.options.configure.args = " -DR_EXECUTABLE=" + os.path.join(CraftCore.standardDirs.craftRoot(), "lib", "R", "R.framework", "Resources", "R")

    def fetch(self):
        # Temporary workaround for failure to pull due to local modification of ver.R. Remove the line below around June, 2018.
        utils.deleteFile(os.path.join(self.checkoutDir(), "rkward", "rbackend", "rpackages", "rkward", "R", "ver.R"))

        ret = CMakePackageBase.fetch(self)
        CraftCore.debug.step("Fetching translations")
        RKTranslations(self).fetch()
        return ret

    def install(self):
        ret = CMakePackageBase.install(self)
        if OsUtils.isWin():
            # Make installation movable, by providing rkward.ini with relative path to R
            rkward_ini = open(os.path.join(self.imageDir(), "bin", "rkward.ini"), "w")
            if CraftCore.compiler.isX64():
                rkward_ini.write("R executable=../lib/R/bin/x64/R.exe\n")
            else:
                rkward_ini.write("R executable=../lib/R/bin/i386/R.exe\n")
            rkward_ini.close()
        return ret

    def msvcconfigure(self):
        # Need to create a .lib-file for R.dll, first
        dump = subprocess.check_output(["dumpbin", "/exports", os.path.join(self.r_dir, "R.dll")]).decode(
            "latin1").splitlines()
        exports = []
        for line in dump:
            fields = line.split()
            if len(fields) != 4:
                continue
            exports.append(fields[3])
        self.enterBuildDir()
        deffile = open(os.path.join(self.buildDir(), "R.def"), 'w')
        deffile.write("EXPORTS\r\n")
        deffile.write("\r\n".join(exports) + "\r\n")
        deffile.close()
        subprocess.call(["lib", "/def:R.def", "/out:R.lib", "/machine:x86"])

        # Now configure as usual.
        return self.realconfigure()

    def createPackage(self):
        self.defines["productname"] = "RKWard"
        self.defines["executable"] = "bin\\rkward.exe"
        self.defines["icon"] = os.path.join(self.sourceDir(), "rkward", "icons", "app-icon", "rkward.ico")

        self.ignoredPackages.append("binary/mysql")
        self.ignoredPackages.append("data/hunspell-dictionaries")

        return TypePackager.createPackage(self)
