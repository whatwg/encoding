SHELL=/bin/bash -o pipefail
.PHONY: local remote deploy

remote: encoding.bs
	@ (HTTP_STATUS=$$(curl https://api.csswg.org/bikeshed/ \
	                       --output encoding.html \
	                       --write-out "%{http_code}" \
	                       --header "Accept: text/plain, text/html" \
	                       -F die-on=warning \
	                       -F md-Text-Macro="COMMIT-SHA LOCAL COPY" \
	                       -F file=@encoding.bs) && \
	[[ "$$HTTP_STATUS" -eq "200" ]]) || ( \
		echo ""; cat encoding.html; echo ""; \
		rm -f encoding.html; \
		exit 22 \
	);

local: encoding.bs
	bikeshed spec encoding.bs encoding.html --md-Text-Macro="COMMIT-SHA LOCAL-COPY"

deploy: encoding.bs
	curl --remote-name --fail https://resources.whatwg.org/build/deploy.sh
	EXTRA_FILES="*.txt *.json *.css" \
	POST_BUILD_STEP='python visualize.py "$$DIR/"' \
	bash ./deploy.sh
