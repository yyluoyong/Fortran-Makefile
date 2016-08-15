SHELL=/bin/sh

#**********************************************************************************
#编译文件放置位置
buildDir := ./build

#源码位置
#源码存在于多个位置时，以空格隔开即可
#sourceDir := 目录1 目录2
sourceDir := ./src


#源码文件
sourceFiles := $(foreach f90Dir, $(sourceDir), $(wildcard $(f90Dir)/*.f90))

#目标文件
objectFiles := $(patsubst %.f90, $(buildDir)/%.o, $(notdir $(sourceFiles)))

#**********************************************************************************
#**********************************************************************************
#Debian, Redhat, YHKylin
LinuxRelease = $(shell cat /etc/issue | head -n 1 | cut -d " " -f 1)

#选择编译环境
# Ifort         --> Intel ifort 编译
# IntelGfortran --> Intel gfortran 编译
# FeiTeng       --> 飞腾 gfortran 编译
#CompileEnv = Ifort
CompileEnv = IntelGfortran
#CompileEnv = FeiTeng

#根据发行版本选择编译环境
ifeq ($(LinuxRelease), YHKylin)
	CompileEnv = FeiTeng
endif

#编译环境对应的编译命令
#F90        = mpif90 -r8 -f90= ifort
IfortCMD    = ifort -r8
GfortranCMD = gfortran -fdefault-real-8

#编译环境对应的选项
IfortOpt = -module $(buildDir)
GfortranOpt = -J$(buildDir)

#编译环境对应的库
#IfortLibs        = -llapack -lblas
IfortLibs         =
IntelGfortranLibs =
FeiTengLibs       =

#**********************************************************************************

ifeq ($(CompileEnv), Ifort)
	F90     = $(IfortCMD)
	FFLAG   = $(IfortOpt)
	LKFLAGS = $(IfortLibs)
else ifeq ($(CompileEnv), IntelGfortran)
	F90     = $(GfortranCMD)
	FFLAG   = $(GfortranOpt)
	LKFLAGS = $(IntelGfortranLibs)
else
	F90     = $(GfortranCMD)
	FFLAG   = $(GfortranOpt)
	LKFLAGS = $(FeiTengLibs)
endif


#终极目标文件
EXEC := main

#终极目标
$(EXEC): $(objectFiles)
	$(F90) $^ $(LKFLAGS) -o $@

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
	$(F90) $(FFLAG)   -c  $<    -o  $@

#生成依赖文件
$(buildDir)/fortranDependency.d : $(sourceFiles) fortranDependency.py
	@mkdir -p $(dir $@)
	python fortranDependency.py $(sourceDir) > $@

#导入依赖关系
-include $(buildDir)/fortranDependency.d
