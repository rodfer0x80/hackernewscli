.PHONY: run
run:
	scripts/run.py

.PHONY: build
build:
	scripts/build.sh

.PHONY: clean
clean:
	scripts/clean.sh

.PHONY: deploy
deploy:
	scripts/deploy.py

.PHONY: freshrun
freshrun:
	scripts/freshrun.py
