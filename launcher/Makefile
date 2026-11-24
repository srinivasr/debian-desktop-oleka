PREFIX ?= /usr/local
LIBDIR = $(PREFIX)/lib/oleka-launcher
DATADIR = $(PREFIX)/share/oleka-launcher

.PHONY: test run install uninstall

test:
	python3 -m pytest -q tests

run:
	python3 -m olekalauncher

install:
	install -d $(DESTDIR)$(LIBDIR)/olekalauncher $(DESTDIR)$(DATADIR) $(DESTDIR)$(PREFIX)/bin
	install -m 644 olekalauncher/*.py $(DESTDIR)$(LIBDIR)/olekalauncher/
	install -m 644 style.css $(DESTDIR)$(DATADIR)/style.css
	printf '#!/bin/sh\nPYTHONPATH=$(LIBDIR) exec python3 -m olekalauncher "$$@"\n' > $(DESTDIR)$(PREFIX)/bin/oleka-launcher
	chmod 755 $(DESTDIR)$(PREFIX)/bin/oleka-launcher

uninstall:
	rm -rf $(LIBDIR) $(DATADIR) $(PREFIX)/bin/oleka-launcher
