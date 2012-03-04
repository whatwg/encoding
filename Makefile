ANOLIS = anolis

all: Overview.html data/xrefs/network/encoding.json

Overview.html: Overview.src.html data Makefile
	$(ANOLIS) --omit-optional-tags --quote-attr-values \
	--enable=xspecxref --enable=refs $< $@

data/xrefs/network/encoding.json: Overview.src.html Makefile
	$(ANOLIS) --dump-xrefs=$@ $< /tmp/spec
