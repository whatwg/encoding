local: encoding.bs
	bikeshed spec encoding.bs encoding.html --md-Text-Macro="SNAPSHOT-LINK LOCAL COPY"

remote: encoding.bs
	curl https://api.csswg.org/bikeshed/ -f -F file=@encoding.bs > encoding.html -F md-Text-Macro="SNAPSHOT-LINK LOCAL COPY"

deploy: encoding.bs
	curl --remote-name --fail https://resources.whatwg.org/build/deploy.sh && bash ./deploy.sh
