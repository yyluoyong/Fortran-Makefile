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

#编译命令
F90 = mpif90 -r8 -f90=ifort

#编译选项，设置模块放置位置
FFLAG = -module $(buildDir)

#链接选项
LKFLAGS =

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
