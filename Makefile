SHELL=/bin/bash -o pipefail

remote: encoding.bs
	curl https://api.csswg.org/bikeshed/ -f -F file=@encoding.bs > encoding.html -F md-Text-Macro="SNAPSHOT-LINK LOCAL COPY"

local: encoding.bs
	bikeshed spec encoding.bs encoding.html --md-Text-Macro="SNAPSHOT-LINK LOCAL COPY"

deploy: encoding.bs
	curl --remote-name --fail https://resources.whatwg.org/build/deploy.sh
	CHECKER_FILTER="Text run is not in Unicode Normalization Form C\.|.*appears to be written in.*|.*Charmod C073.*" \
	EXTRA_FILES="*.txt *.json *.css" \
	POST_BUILD_STEP='python visualize.py "$$DIR/"' \
	bash ./deploy.sh

review: encoding.bs
	curl --remote-name --fail https://resources.whatwg.org/build/review.sh
	bash ./review.sh
