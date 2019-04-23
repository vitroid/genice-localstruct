.DELETE_ON_ERROR:

all: README.md



test-deploy: build
	twine upload -r pypitest dist/*
test-install:
	pip install pillow
	pip install --index-url https://test.pypi.org/simple/ genice_localstruct



install:
	./setup.py install
uninstall:
	-pip uninstall -y genice-localstruct
build: README.md $(wildcard genice_localstruct/formats*.py)
	./setup.py sdist bdist_wheel


deploy: build
	twine upload dist/*
check:
	./setup.py check
clean:
	-rm $(ALL) *~ */*~ 
	-rm -rf build dist *.egg-info
	-find . -name __pycache__ | xargs rm -rf
