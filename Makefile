include make.inc

#*********************************************************************************
#编译文件放置位置
buildDir := ./build

#源码位置
sourceDir := ./src

#源码文件
sourceFiles := $(foreach f90Dir, $(sourceDir), $(wildcard $(f90Dir)/*.f90))

#目标文件
objectFiles := $(patsubst %.f90, $(buildDir)/%.o, $(notdir $(sourceFiles)))
#*********************************************************************************

#*********************************************************************************
#主程序生成需要所有的.o文件
#所有源码位置
allSourceDir := ./ 

#所有源码文件
allSourceFiles := $(foreach f90Dir, $(allSourceDir), $(wildcard $(f90Dir)*.f90))

#所有的.o文件
#所有的.o文件位置都按照如下规则生成: 源码文件所在目录/build/xxx.o
allObjectFiles := $(foreach f90, $(allSourceFiles), $(dir $(f90))build/$(basename $(notdir $(f90))).o)
#*********************************************************************************

#可执行文件
EXEC := main

#终极目标
all: $(EXEC)

#生成可执行文件
$(EXEC): $(objectFiles)
	$(F90) $(allObjectFiles) $(LKFLAGS) -o $@

#伪目标
.PHONY: clean run

#清理编译产生的中间文件
clean:
	-rm -rf $(buildDir)
	-rm $(EXEC)

#执行
run:
	@echo '执行脚本 "Run.sh"，请确保 "Run.sh" 的可执行权限，添加可执行权限的命令为 "chmod +x Run.sh"'
	@./Run.sh

#.o文件的模式规则
$(buildDir)/%.o : $<
	@mkdir -p $(dir $@)
	$(F90) $(FFLAG) $(LKFLAGS)   -c  $<    -o  $@

#生成依赖文件
$(buildDir)/fortranDependency.d : $(allSourceFiles) fortranDependency.py
	@mkdir -p $(dir $@)
	python fortranDependency.py $(sourceDir) $(targetDir) > $@

#导入依赖关系
-include $(buildDir)/fortranDependency.d
