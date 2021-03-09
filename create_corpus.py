"""
Creates a corpus from Wikipedia dump file.

Inspired by:
https://github.com/panyang/Wikipedia_Word2vec/blob/master/v1/process_wiki.py
"""

import sys
import time
from gensim.corpora import WikiCorpus

def make_corpus(in_f, out_f):

	"""Convert Wikipedia xml dump file to text corpus"""

	output = open(out_f, 'w')
	print("assigning wiki")
	start_time = time.time()
	wiki = WikiCorpus(in_f)

	print("wiki assigned in %s seconds" % (time.time() - start_time))

	i = 0
	for text in wiki.get_texts():
		output.write(bytes(' '.join(text), 'utf-8').decode('utf-8') + '\n')
		i = i + 1
		if (i % 1000 == 0):
			print('Processed ' + str(i) + ' articles')
	output.close()
	print('Processing complete! Total: ' + str(i) + ' articles processed')


if __name__ == '__main__':
	start_time = time.time()
	if len(sys.argv) != 3:
		print('Usage: python make_wiki_corpus.py <wikipedia_dump_file> <processed_text_file>')
		sys.exit(1)
	in_f = sys.argv[1]
	out_f = sys.argv[2]
	make_corpus(in_f, out_f)
	print("--- %s seconds ---" % (time.time() - start_time))