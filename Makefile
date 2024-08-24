
OBJDIR=bin
SRCDIR=src
WWWDIR=www

WWWOBJDIR=$(OBJDIR)/$(WWWDIR)

ifndef $(TARGET)
	TARGET=all
endif


SOURCES := $(shell find $(SRCDIR) -name '*.py')
OBJS    := $(subst $(SRCDIR),$(OBJDIR),$(SOURCES:%.py=%.mpy))
WEB     := www/cfg.js www/cfg.css www/index.html
WEBOBJS := $(subst $(WWWDIR),$(WWWOBJDIR),$(WEB))

all: mpy

mpy: $(OBJS) $(WEBOBJS) $(OBJDIR)/secrets/factory.ini
	echo "piss"

$(OBJDIR)/secrets/factory.ini: defaults/factory.ini
	@mkdir -p $(@D)
	cp $< $@

$(OBJDIR):
	mkdir -p $@

$(WEBOBJS): $(WEB)
	@mkdir -p $(@D)
	cp $< $@

$(OBJDIR)/%.mpy: $(addprefix $(SRCDIR)/,%.py)
	@mkdir -p $(@D)
	./private/mpy-cross -o $@ $<
