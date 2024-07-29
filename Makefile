
OBJDIR=bin
SRCDIR=src

ifndef $(TARGET)
	TARGET=all
endif


SOURCES := $(shell find $(SRCDIR) -name '*.py')

OBJS    := $(subst $(SRCDIR),$(OBJDIR),$(SOURCES:%.py=%.mpy))

all: mpy

mpy: $(OBJS)
	echo $(SOURCES)
	echo $(OBJS)


$(OBJDIR):
	mkdir -p $@

$(OBJDIR)/%.mpy: $(addprefix $(SRCDIR)/,%.py)
	@mkdir -p $(@D)
	./private/mpy-cross -o $@ $<
