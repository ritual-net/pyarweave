release: ensure-git pypi_upload

help:
	@echo 'Target name is simply passed to setup.py . make build, make install, make bdist_wheel ...'

%:
	python3 setup.py "$@"

ensure-git:
	git update-index --refresh 
	git diff-index --quiet HEAD --
	git push
