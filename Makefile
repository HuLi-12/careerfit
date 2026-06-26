.PHONY: format test run clean package validate

format:
	black src/ tests/

test:
	python -m unittest discover -s tests -v

run:
	python src/main.py --input examples/input_match_analysis.txt

run-json:
	python src/main.py --input examples/input_match_analysis.txt --format json

validate:
	python scripts/validate_skill.py

package:
	powershell -Command "Compress-Archive -Path SKILL.md, README.md, requirements.txt, src, examples, tests, docs, pyproject.toml -DestinationPath careerfit-evidence-skill.zip -Force"

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache
	rm -rf *.egg-info dist build
