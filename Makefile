
OBJDIR=bin
SRCDIR=src
WWWDIR=www

PRIVATEDIR=private

WWWOBJDIR=$(OBJDIR)/$(WWWDIR)

MPYCROSS=$(PRIVATEDIR)/mpy-cross

ifndef $(TARGET)
	TARGET=all
endif



SOURCES := $(shell find $(SRCDIR) -name '*.py')
OBJS    := $(subst $(SRCDIR),$(OBJDIR),$(SOURCES:%.py=%.mpy))
WEBOBJS := $(OBJDIR)/$(WWWDIR)/index.html

all: mpy mock

mpy: $(OBJS) $(WEBOBJS) $(OBJDIR)/secrets/factory.ini
	git log -1 --pretty=format:"GIT = \"%H\"" > $(OBJDIR)/git.py

$(OBJDIR)/secrets/factory.ini: defaults/factory.ini
	@mkdir -p $(@D)
	cp $< $@

$(OBJDIR)/$(WWWDIR)/index.html: $(OBJDIR)/$(WWWDIR) $(WWWDIR)/index.html $(WWWDIR)/cfg.js $(WWWDIR)/cfg.css
	python3 webbundle.py $(OBJDIR)/$(WWWDIR)/index.html

$(OBJDIR)/$(WWWDIR):
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
TESTWEBOBJS := $(MOCKDIR)/$(WWWDIR)/index.html

mock: $(TESTPYS) $(TESTWEBOBJS) $(MOCKDIR)/secrets/factory.ini
	git log -1 --pretty=format:"GIT = \"%H\"" > $(MOCKDIR)/git.py

$(PRIVATEDIR):
	mkdir -p $@

$(MOCKDIR):
	mkdir -p $@

$(MOCKDIR)/secrets/factory.ini: defaults/factory.ini
	@mkdir -p $(@D)
	cp $< $@

$(MOCKDIR)/$(WWWDIR)/index.html: $(MOCKDIR)/$(WWWDIR) $(WWWDIR)/index.html $(WWWDIR)/cfg.js $(WWWDIR)/cfg.css
	python3 webbundle.py $(MOCKDIR)/$(WWWDIR)/index.html

$(MOCKDIR)/$(WWWDIR):
	mkdir -p $@

$(MOCKDIR)/%.py: $(addprefix $(SRCDIR)/,%.py)
	@mkdir -p $(@D)
	cp $< $@