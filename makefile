all.pdf: all.md
	pandoc --filter	 tikz.py  --lua-filter=abc.lua --top-level-division=chapter -t pdf -o all.pdf all.md

all.md: pages/0*.md
	./joiner.pl

all.tex: all.md
	pandoc --filter	 tikz.py --lua-filter=abc.lua --top-level-division=chapter -t latex -o all.tex all.md
