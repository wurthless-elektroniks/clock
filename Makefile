
OBJDIR=bin
SRCDIR=src
WWWDIR=www

PRIVATEDIR=private

WWWOBJDIR=$(OBJDIR)/$(WWWDIR)

ifndef $(TARGET)
	TARGET=all
endif



SOURCES := $(shell find $(SRCDIR) -name '*.py')
OBJS    := $(subst $(SRCDIR),$(OBJDIR),$(SOURCES:%.py=%.mpy))
WEBOBJS := $(OBJDIR)/$(WWWDIR)/index.html $(OBJDIR)/$(WWWDIR)/cfg.css $(OBJDIR)/$(WWWDIR)/cfg.js

all: mpy mock

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

$(OBJDIR)/%.mpy: $(addprefix $(SRCDIR)/,%.py) $(PRIVATEDIR)/mpy-cross
	@mkdir -p $(@D)
	$(MPYCROSS) -o $@ $<

# ------------------------------------------
# mock environment
# ------------------------------------------
MOCKDIR = $(PRIVATEDIR)/test

TESTPYS    := $(subst $(SRCDIR),$(MOCKDIR),$(SOURCES:%.py=%.py))
TESTWEBOBJS := $(MOCKDIR)/$(WWWDIR)/index.html $(MOCKDIR)/$(WWWDIR)/cfg.css $(MOCKDIR)/$(WWWDIR)/cfg.js
mock: $(TESTPYS) $(TESTWEBOBJS) $(MOCKDIR)/secrets/factory.ini

$(PRIVATEDIR):
	mkdir -p $@

$(MOCKDIR):
	mkdir -p $@

$(MOCKDIR)/secrets/factory.ini: defaults/factory.ini
	@mkdir -p $(@D)
	cp $< $@

$(MOCKDIR)/$(WWWDIR)/%.html: $(WWWDIR)/%.html $(MOCKDIR)/$(WWWDIR)
	cp $< $@

$(MOCKDIR)/$(WWWDIR)/%.css: $(WWWDIR)/%.css $(MOCKDIR)/$(WWWDIR)
	cp $< $@

$(MOCKDIR)/$(WWWDIR)/%.js: $(WWWDIR)/%.js $(MOCKDIR)/$(WWWDIR)
	cp $< $@

$(MOCKDIR)/$(WWWDIR): $
	mkdir -p $@

$(MOCKDIR)/%.py: $(addprefix $(SRCDIR)/,%.py)
	@mkdir -p $(@D)
	cp $< $@
