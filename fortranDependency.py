#-*- coding: UTF-8 -*-
import os
import re
import sys

class FortranFileDependency:

    def __init__(self, buildDir="build/", sourceFilePath="", sourceDir=["./src"], \
                 targetDir=["./src"], targetTypes=[".f90", ".F90"], commentChar="!"):

        #编译文件放置位置
        self.__buildDir = buildDir

        #需要分析依赖关系的单个文件路径
        self.__sourceFilePath = sourceFilePath

        #需要分析依赖关系的源码文件所在位置
        self.__sourceDir = sourceDir

        #sourceDir目录中的文件所依赖的文件所在位置
        self.__targetDir = targetDir

        #目标路径
        self.__targetTypes = targetTypes

        #注释符
        self.__commentChar = commentChar

        #文件包含的module，{key:set()}
        self.__filesContainModule = {}

        #文件使用的module，{key:set()}
        self.__filesUsedModule = {}


    #提取每行使用的module
    def __getConModInLine(self, line):
        line = line.lower().strip()
        regModule = re.compile("^\s*module\s+")

        if regModule.match(line):
            moduleName = re.split("\s", line)[1]
            #去除注释部分
            moduleName = re.sub("!.*", "", moduleName)

            return moduleName
        else:
            return ""

    #提取每一行提供的module
    def __getUsedModInLine(self, line):
        line = line.lower().strip()
        regModule = re.compile("^\s*use\s+")

        if regModule.match(line):
            moduleName = re.split("\s", line)[1]
            # 去除注释部分和逗号选用部分
            moduleName = re.sub("[,!].*", "", moduleName)

            # mpi库不包含在内
            if moduleName == "mpi":
                return ""

            return moduleName
        else:
            return ""

    #获得源码文件提供的module名字
    def __getConModInFile(self, filePath):
        fileObeject = open(filePath, 'r')

        #该文件包含的module
        providedModules = set()

        try:
            for line in fileObeject:
                moduleName = self.__getConModInLine(line)

                if moduleName != "":
                    providedModules.add(moduleName)
        finally:
            fileObeject.close()

        self.__filesContainModule[filePath] = providedModules


    #获得源码文件使用的module名字
    def __getUsedModInFile(self, filePath):
        fileObeject = open(filePath, 'r')

        #该文件使用的module
        usedModules = set()

        try:
            for line in fileObeject:
                moduleName = self.__getConModInLine(line)

                moduleName = self.__getUsedModInLine(line)

                if moduleName != "":
                    usedModules.add(moduleName)
        finally:
            fileObeject.close()

        self.__filesUsedModule[filePath] = usedModules


    #获取目录中所有文件包含的module
    def __getConModInDir(self, Dirs):

        #遍历所有指定目录,获得文件提供的module字典
        for targetDir in Dirs:
            #遍历该目录的所有文件
            for fortranFileName in os.listdir(targetDir):
                fortranFilePath = os.path.join(targetDir, fortranFileName)
                if(os.path.isfile(fortranFilePath)):
                    fortranFileType = os.path.splitext(fortranFileName)[-1]
                    #匹配Fortran格式文件
                    for targetType in self.__targetTypes:
                        if targetType == fortranFileType:
                            self.__getConModInFile(fortranFilePath)

    #获取目录中所有文件使用的module
    def __getUsedModInDir(self, Dirs):
        # 遍历所有指定目录
        for targetDir in Dirs:
            # 遍历该目录的所有文件
            for fortranFileName in os.listdir(targetDir):
                fortranFilePath = os.path.join(targetDir, fortranFileName)
                if (os.path.isfile(fortranFilePath)):
                    fortranFileType = os.path.splitext(fortranFileName)[-1]
                    # 匹配Fortran格式文件
                    for targetType in self.__targetTypes:
                        if targetType == fortranFileType:
                            self.__getUsedModInFile(fortranFilePath)


    #获得依赖关系
    def getDependency(self):

        self.__getConModInDir(self.__targetDir)

        if self.__sourceFilePath != "":
            self.__getUsedModInFile(self.__sourceFilePath)
        else:
            self.__getUsedModInDir(self.__sourceDir)

        #保存依赖关系的字典
        dependencyDict = {}

        #遍历所有文件
        for fileUsed in self.__filesUsedModule:

            #该文件的.o文件依赖于源文件本身
            fileUsedOFile = re.sub(".[fF]90$", ".o", os.path.basename(fileUsed))
            fileUsedBuildFile = os.path.join(self.__buildDir, fileUsedOFile)
            dependencyDict[fileUsedBuildFile] = [fileUsed]

            #遍历该文件使用的所有module
            for usedModule in self.__filesUsedModule[fileUsed]:
                #遍历所有文件，搜索该module出自哪个文件
                for fileContain in self.__filesContainModule:
                    if fileUsed != fileContain:
                        #找到之，即 fileUsed 依赖于 fileContain
                        if usedModule in self.__filesContainModule[fileContain]:
                            fileContainBaseName = os.path.basename(fileContain)
                            fileContainPath = os.path.dirname(fileContain)
                            fileContainOFile = re.sub(".[fF]90$", ".o", fileContainBaseName)
                            fileContainBuildFile = os.path.join(fileContainPath, self.__buildDir, fileContainOFile)

                            #防止重复
                            if fileContainBuildFile not in dependencyDict[fileUsedBuildFile]:
                                dependencyDict[fileUsedBuildFile].append(fileContainBuildFile)

        return dependencyDict


def main(dirArgs):

    if os.path.isfile(dirArgs[0]):
        fortranDependency = FortranFileDependency(sourceFilePath=dirArgs[0], targetDir=dirArgs[1:])
    else:
        fortranDependency = FortranFileDependency(sourceDir=[dirArgs[0]], targetDir=dirArgs[1:])

    dependencyDict = fortranDependency.getDependency()

    for buildFile in dependencyDict:
        dependencyStr = buildFile + " : "
        for dependencyFile in dependencyDict[buildFile]:
            dependencyStr = dependencyStr + dependencyFile + " "

        print(dependencyStr)


if __name__ == '__main__':

    main(sys.argv[1:])