#!/usr/bin/make -f

LEINURL = "https://raw.githubusercontent.com/technomancy/leiningen/stable/bin/lein"
HOME ?= /srv/doedel

build:
	wget $(LEINURL)
	chmod +x lein
	$(MAKE) -C doedel
	$(MAKE) -C fake-doedel

install: build
	install -m 644 -o root doedel/target/doedel.jar $(HOME)
	install -m 644 -o root doedel.md $(HOME)
	install -m 644 -o root systemd/doedel.service /etc/systemd/system
	systemctl enable doedel.service
