#-*- coding: UTF-8 -*-
import os
import re
import sys

class FortranFileDependency:

    def __init__(self, buildDir="./build/", targetDir=["./src"], targetTypes=[".f90", ".F90"], commentChar="!"):

        #编译文件放置位置
        self.__buildDir = buildDir

        #目标路径
        self.__targetDir = targetDir

        #目标路径
        self.__targetTypes = targetTypes

        #注释符
        self.__commentChar = commentChar

        #文件包含的module，{key:set()}
        self.__filesContainModule = {}

        #文件使用的module，{key:set()}
        self.__filesUsedModule = {}

    #生成依赖关系
    def __getModuleData(self, filePath):
        fileObeject = open(filePath, 'r')

        #该文件包含的module
        providedModules = set()
        #该文件使用的module
        usedModules = set()

        try:
            for line in fileObeject:
                #包含的module
                line = line.strip().lower()
                if line.startswith("module"):
                    commentCharIndex = line.find(self.__commentChar)
                    #行后注释
                    if commentCharIndex != -1:
                        lineContent = line[:commentCharIndex]
                    else:
                        lineContent = line
                    #providedModules.add(lineContent.split()[-1].strip()+".mod")
                    providedModules.add(lineContent.split()[-1].strip())
                #使用的module
                elif line.startswith("use"):
                    commentCharIndex = line.find(self.__commentChar)
                    #行后注释
                    if commentCharIndex != -1:
                        lineContent = line[:commentCharIndex]
                    else:
                        lineContent = line

                    #usedModules.add(lineContent.split()[1].split(",")[0].strip()+".mod")
                    oneModule = lineContent.split()[1].split(",")[0].strip()
                    if oneModule == "mpi":
                        continue
                    usedModules.add(oneModule)
        finally:
            fileObeject.close()

        self.__filesContainModule[filePath] = providedModules
        self.__filesUsedModule[filePath] = usedModules


    #生成依赖关系字典
    def __genDependencyDict(self):

        #遍历所有指定目录
        for targetDir in self.__targetDir:
            for fortranFileName in os.listdir(targetDir):
                fortranFilePath = os.path.join(targetDir, fortranFileName)
                if(os.path.isfile(fortranFilePath)):
                    fortranFileType = os.path.splitext(fortranFileName)[-1]
                    for targetType in self.__targetTypes:
                        if targetType == fortranFileType:
                            self.__getModuleData(fortranFilePath)


    #获得依赖关系
    def getDependency(self):

        self.__genDependencyDict()

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
                            fileContainOFile = re.sub(".[fF]90$", ".o", os.path.basename(fileContain))
                            fileContainBuildFile = os.path.join(self.__buildDir, fileContainOFile)

                            #防止重复
                            if fileContainBuildFile not in dependencyDict[fileUsedBuildFile]:
                                dependencyDict[fileUsedBuildFile].append(fileContainBuildFile)

        return dependencyDict


def main(dirArgs):

    fortranDependency = FortranFileDependency(targetDir=dirArgs)

    dependencyDict = fortranDependency.getDependency()

    for buildFile in dependencyDict:
        dependencyStr = buildFile + " : "
        for dependencyFile in dependencyDict[buildFile]:
            dependencyStr = dependencyStr + dependencyFile + " "

        print(dependencyStr)


if __name__ == '__main__':

    main(sys.argv[1:])