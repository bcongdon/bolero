.PHONY: test
test:
	nosetests --with-coverage --cover-package=bolero --cover-html

clean:
	find . -name \*.pyc -delete