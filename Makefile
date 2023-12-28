output/: 
	python3 scraper.py
	mv output/Season_5/5-Dewey\ Wins\"\[12\].txt output/Season_5/5-Dewey\ Wins.txt

clean:
	rm -r output/
