
OBJDIR=bin
SRCDIR=src
WWWDIR=www

WWWOBJDIR=$(OBJDIR)/$(WWWDIR)

ifndef $(TARGET)
	TARGET=all
endif


SOURCES := $(shell find $(SRCDIR) -name '*.py')
OBJS    := $(subst $(SRCDIR),$(OBJDIR),$(SOURCES:%.py=%.mpy))

WEBOBJS := $(OBJDIR)/$(WWWDIR)/index.html $(OBJDIR)/$(WWWDIR)/cfg.css $(OBJDIR)/$(WWWDIR)/cfg.js

all: mpy

mpy: $(OBJS) $(WEBOBJS) $(OBJDIR)/secrets/factory.ini

$(OBJDIR)/secrets/factory.ini: defaults/factory.ini
	@mkdir -p $(@D)
	cp $< $@

$(OBJDIR)/$(WWWDIR)/%.html: $(WWWDIR)/%.html $(OBJDIR)/$(WWWDIR)
	cp $< $@

$(OBJDIR)/$(WWWDIR)/%.css: $(WWWDIR)/%.css $(OBJDIR)/$(WWWDIR)
	cp $< $@

$(OBJDIR)/$(WWWDIR)/%.js: $(WWWDIR)/%.js $(OBJDIR)/$(WWWDIR)
	cp $< $@

$(OBJDIR)/$(WWWDIR): $
	mkdir -p $@

$(OBJDIR):
	mkdir -p $@


$(OBJDIR)/%.mpy: $(addprefix $(SRCDIR)/,%.py)
	@mkdir -p $(@D)
	./private/mpy-cross -o $@ $<
