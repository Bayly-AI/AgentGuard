.PHONY: install test test-pre-deploy test-post-deploy

install:
	python3 -m pip install -e ".[dev]"

test:
	python3 -m pytest -v

test-pre-deploy:
	python3 -m pytest -v --cov=agentguard --cov-report=xml

test-post-deploy:
	python3 -c "import agentguard; print('AgentGuard post-deploy check OK')"
