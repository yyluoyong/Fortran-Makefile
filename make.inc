SHELL=/bin/sh

#模块文件存放位置
modDir := ./build

#*********************************************************************************
#Debian, Redhat, YHKylin
LinuxRelease := $(shell cat /etc/issue | head -n 1 | cut -d " " -f 1)

#手动选择编译环境
# DebianIfort --> Debian ifort 编译
# RedhatIfort --> Redhat ifort 编译
# DebianGF    --> Debian gfortran 编译
# RedhatGF    --> Redhat gfortran 编译
# FeiTengGF   --> 飞腾 gfortran 编译
#CompileEnv := DebianIfort
#CompileEnv := RedhatIfort
#默认是Debian gfortran编译环境
CompileEnv := DebianGF
#CompileEnv := RedhatGF
#CompileEnv := FeiTengGF

#根据发行版本自动选择编译环境
ifeq ($(LinuxRelease), YHKylin)
	CompileEnv := FeiTengGF
else ifeq ($(LinuxRelease), Debian)
	CompileEnv := DebianGF
else ifeq ($(LinuxRelease), Red)
	CompileEnv := RedhatGF
endif

#不同平台下ifort, gfortran的路径
DebianIfortPath := ifort
RedhatIfortPath := ifort
DebianGFPath    := gfortran
RedhatGFPath    := gfortran
FeiTengGFPath   := gfortran

#不同编译环境对应的选项
DebianIfortOpt := -module $(modDir) -r8
RedhatIfortOpt := -module $(modDir) -r8
DebianGFOpt    := -J$(modDir) -fdefault-real-8 -fdefault-double-8
RedhatGFOpt    := -J$(modDir) -fdefault-real-8 -fdefault-double-8
FeiTengGFOpt   := -J$(modDir) -fdefault-real-8 -fdefault-double-8

#不同编译环境的编译命令
DebianIfortCMD := $(DebianIfortPath) 
RedhatIfortCMD := $(RedhatIfortPath)
DebianGFCMD    := $(DebianGFPath)
RedhatGFCMD    := $(RedhatGFPath)
FeiTengGFCMD   := $(FeiTengGFPath)

#不同编译环境对应的库
DebianIfortLibs :=  
RedhatIfortLibs := 
DebianGFLibs    := 
RedhatGFLibs    := 
FeiTengGFLibs   := 

#*********************************************************************************

ifeq ($(CompileEnv), DebianIfort)
	F90     := $(DebianIfortCMD)
	FFLAG   := $(DebianIfortOpt)
	LKFLAGS := $(DebianIfortLibs)
else ifeq ($(CompileEnv), DebianGF)
	F90     := $(DebianGFCMD)
	FFLAG   := $(DebianGFOpt)
	LKFLAGS := $(DebianGFLibs)
else ifeq ($(CompileEnv), RedhatIfort)
	F90     := $(RedhatIfortCMD)
	FFLAG   := $(RedhatIfortOpt)
	LKFLAGS := $(RedhatIfortLibs)
else ifeq ($(CompileEnv), RedhatGF)
	F90     := $(RedhatGFCMD)
	FFLAG   := $(RedhatGFOpt)
	LKFLAGS := $(RedhatGFLibs)
#	自己编译的需指出相应的lib和lib64, 或者保证这些库在搜索路径下
#	LD_LIBRARY_PATH := 
else ifeq ($(CompileEnv), FeiTengGF)
	F90     := $(FeiTengGFCMD)
	FFLAG   := $(FeiTengGFOpt)
	LKFLAGS := $(FeiTengGFLibs)
endif
