all.pdf: all.md
	pandoc --filter	 tikz.py --top-level-division=chapter -t pdf -o all.pdf all.md

all.md: 0*.md fig*png
	./joiner.pl

all.tex: all.md
	pandoc --filter	 tikz.py --top-level-division=chapter -t latex -o all.tex all.md
