local: encoding.bs
	bikeshed

remote: encoding.bs
	curl https://api.csswg.org/bikeshed/ -f -F file=@encoding.bs > encoding.html
