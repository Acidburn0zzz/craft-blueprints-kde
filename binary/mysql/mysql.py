import shutil

import info
from Package.BinaryPackageBase import *

class subinfo(info.infoclass):
    def setTargets(self):
        if self.options.dynamic.useMariaDB:
            self.setMariaDbTargets()
        else:
            self.setMySqlTargets()

    def setMariaDbTargets(self):
        baseURL = "http://mariadb.kisiek.net/"
        ver = '10.2.12'
        arch = "x64" if CraftCore.compiler.isX64() else "32"
        self.targets[ver] = f"{baseURL}mariadb-{ver}/win{arch}-packages/mariadb-{ver}-win{arch}.zip"
        self.targetInstSrc[ver] = f"mariadb-{ver}-win{arch}"

        self.targetDigests[ver] = (['1e6a5640a9b9e9c290f785f232ab3f623bfc5f8736e26e8ae040c0d7dde174ae'],
                                   CraftHash.HashAlgorithm.SHA256)
        self.targetDigestsX64[ver] = (['b57cc78fe79633e551d88622bfa729328268da5e7b0fa58e86e838fcc906c796'],
                                      CraftHash.HashAlgorithm.SHA256)

        self.description = "MariaDB database server and embedded library"
        self.defaultTarget = ver

    def setMySqlTargets(self):
        baseURL = "http://dev.mysql.com/get/Downloads/MySQL-5.7/"
        ver = '5.7.18'
        if CraftCore.compiler.isX64():
            arch = "x64"
        else:
            arch = "32"
        self.targets[ver] = f"{baseURL}mysql-{ver}-win{arch}.zip"
        self.targetInstSrc[ver] = f"mysql-{ver}-win{arch}"

        self.targetDigestsX64["5.7.18"] = (['6a3b2d070200ae4e29f8a08aceb1c76cca9beccb037de4f5ab120d657e781353'], CraftHash.HashAlgorithm.SHA256)

        self.description = "MySql database server and embedded library"
        self.defaultTarget = ver

    def registerOptions(self):
        self.options.dynamic.registerOption("useMariaDB", False)

    def setDependencies(self):
        self.runtimeDependencies["virtual/base"] = "default"


class Package(BinaryPackageBase):
    def __init__(self):
        BinaryPackageBase.__init__(self)
        self.subinfo.options.package.disableStriping = True
        self.subinfo.options.package.packSources = False

    def install(self):
        shutil.copytree(os.path.join(self.sourceDir(), "bin"), os.path.join(self.installDir(), "bin"),
                        ignore=shutil.ignore_patterns('*.pdb', '*.map', '*test*', 'mysqld-debug.exe', 'echo.exe', '*.pl', 'debug*'))
        shutil.copytree(os.path.join(self.sourceDir(), "lib", "plugin"), os.path.join(self.installDir(), "lib", "plugin"),
                        ignore=shutil.ignore_patterns('*.pdb', '*.map', 'debug*'))
        shutil.copytree(os.path.join(self.sourceDir(), "include"), os.path.join(self.installDir(), "include"),
                        ignore=shutil.ignore_patterns('*.def'))
        shutil.copytree(os.path.join(self.sourceDir(), "share"), os.path.join(self.installDir(), "share"),
                        ignore=shutil.ignore_patterns('Makefile*'))

        if self.subinfo.options.dynamic.useMariaDB:
            utils.copyFile(os.path.join(self.sourceDir(), "lib", f"mariadbclient.lib"), os.path.join(self.installDir(), "lib"))
            utils.copyFile(os.path.join(self.sourceDir(), "lib", f"libmariadb.lib"), os.path.join(self.installDir(), "lib"))
            utils.copyFile(os.path.join(self.sourceDir(), "lib", f"libmariadb.dll"), os.path.join(self.installDir(), "bin"))
            if CraftCore.compiler.isMinGW():
                utils.createImportLibs(f"libmariadb", self.installDir())
        else:
            utils.copyFile(os.path.join(self.sourceDir(), "lib", f"mysqlclient.lib"), os.path.join(self.installDir(), "lib"))
            utils.copyFile(os.path.join(self.sourceDir(), "lib", f"libmysql.lib"), os.path.join(self.installDir(), "lib"))
            utils.copyFile(os.path.join(self.sourceDir(), "lib", f"libmysqld.lib"), os.path.join(self.installDir(), "lib"))
            utils.copyFile(os.path.join(self.sourceDir(), "lib", f"libmysqld.dll"), os.path.join(self.installDir(), "bin"))
            utils.copyFile(os.path.join(self.sourceDir(), "lib", f"libmysql.dll"), os.path.join(self.installDir(), "bin"))
            if CraftCore.compiler.isMinGW():
                utils.createImportLibs(f"libmysqld", self.installDir())
                utils.createImportLibs(f"libmysql", self.installDir())
        return True

    def qmerge(self):
        if not BinaryPackageBase.qmerge(self):
            return False
        datadir = os.path.join(os.path.join(CraftStandardDirs.craftRoot(), "data"))
        if self.subinfo.options.dynamic.useMariaDB:
            return utils.system(["mysql_install_db", f"--datadir={datadir}"])
        else:
            if os.path.isdir(datadir) and len(os.listdir(datadir)) != 0:
                return True
            return utils.system(["mysqld", "--console", "--initialize-insecure"])
