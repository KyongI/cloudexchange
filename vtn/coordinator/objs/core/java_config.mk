##
## Build configuration for Java.
## This file must be included after config.mk.
##

ANT_PATH		:= /usr/bin/ant
ANT_HOME		:= /usr/share/ant
INST_JARDIR		:= $(INST_JAVADIR)/jar
JAVA_DEBUG_DEF		:= 1
JAVA_ENCODING_DEF		:= utf-8
JAVA_HOME		:= /usr/lib/jvm/java-openjdk
JAVA_MODE		:= -d64
JAVA_OBJDIR		:= /usr/local/vtn/vtn/coordinator/objs/jobjs
JNI_INCDIR		:= /usr/lib/jvm/java-openjdk/include/linux /usr/lib/jvm/java-openjdk/include
