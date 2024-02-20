init:
	pip3 install -r requirements.txt

coverage:
	sh scripts/coverage.sh

test: coverage

sdist:
	python setup.py sdist

clean:
	rm -rf build dist .egg *.egg-info

upload:
	twine upload dist/* --verbose

package: sdist upload clean
