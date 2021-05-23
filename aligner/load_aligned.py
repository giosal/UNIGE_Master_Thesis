import os
import time
import argparse
import sys
from bs4 import BeautifulSoup

def write_file(f, doc):
    d = doc
    with open(f, 'w') as file_writer:
        file_writer.write(str(d))
        file_writer.close()

def save_docs(src_doc, target_doc, src_lang, target_lang, out_dir, file_count):
    src_path = os.path.join(out_dir, src_lang)
    target_path = os.path.join(out_dir, target_lang)
    file_name = "doc_{:06d}.txt".format(file_count)
    src_out = os.path.join(src_path, file_name)
    target_out = os.path.join(target_path, file_name)
    write_file(src_out, src_doc)
    write_file(target_out, target_doc)

def load_aligned(aligned_dir):
    st = time.time()
    aligned = list()
    print(aligned_dir)
    for subdir, s, files in sorted(os.walk(aligned_dir)):
        for f in files:
            aligned_file = os.path.join(subdir, f)
            print("file: " + aligned_file)
            with open(aligned_file, encoding="utf-8") as aligned_reader:
                text = aligned_reader.read().split(', ')
                aligned.append(text)
    print("reading aligned files completed successfully in %s seconds" % (time.time() - st))
    return aligned

def read_file(file, doc_id):
    with open(file) as doc:
        text = doc.read()
        soup = BeautifulSoup(text, 'html.parser')
        docs = soup.find_all('doc')
        for d in docs:
            if d.get('id') == doc_id:
                result = d.string
        
    doc.close()
    return result

def read_texts(src_lang, target_lang, src_corpus, target_corpus, aligned_dir, out_dir):
    st = time.time()
    print("aligning documents ...")
    print("corpus size: {0} documents".format(len(src_corpus)))

    count = 0
    for i in range(len(src_corpus)):
        src_doc = read_file(src_corpus[i][len(src_corpus[i])-1], src_corpus[i][0])
        target_doc = read_file(target_corpus[i][len(target_corpus[i])-1], target_corpus[i][0])
        save_docs(src_doc, target_doc, src_lang, target_lang, out_dir, count)
        count += 1
        sys.stdout.write("\r docoments processed: {0}\t\t {1} %".format(count, str(round((count/len(src_corpus)*100),2))))
        sys.stdout.flush()
    print("\nwriting documents completed successfully in %s seconds" % (time.time() - st))

def main(src_lang, target_lang, src_corpus_dir, target_corpus_dir, aligned_dir, out_dir):
    start_time = time.time()
    print('source language: ', src_lang)
    print('target language: ', target_lang)
    print('source corpus directory: ', src_corpus_dir)
    print('target corpus directory: ', target_corpus_dir)
    print('aligned corpus directory: ', aligned_dir)
    print('output directory: ', out_dir)

    src_path = os.path.join(out_dir, src_lang)
    target_path = os.path.join(out_dir, target_lang)
    if not os.path.exists(src_path): os.makedirs(src_path)
    if not os.path.exists(target_path): os.makedirs(target_path)

    src_corpus = load_aligned(os.path.join(aligned_dir, src_lang))
    target_corpus = load_aligned(os.path.join(aligned_dir, target_lang))
    print("source and target corpus loaded successfully")

    read_texts(src_lang, target_lang, src_corpus, target_corpus, aligned_dir, out_dir)

    print("main function completed in %s seconds" % (time.time() - start_time))



parser = argparse.ArgumentParser(description='Align Wikipedia documents based on interlanguage links .')

parser.add_argument('--src-lang', type=str, help='source language. '
                                                'e.g., ar for Arabic, '
                                                'en for English, or '
                                                'fr for French ...', required=True)
parser.add_argument('--target-lang', type=str, help='target language. '
                                                   'e.g., ar for Arabic, '
                                                   'en for English, or '
                                                   'fr for French ...', required=True)
parser.add_argument('--src-corpus', type=str, help='source corpus directory.', required=True)
parser.add_argument('--target-corpus', type=str, help='target corpus directory.', required=True)
parser.add_argument('--aligned-corpus', type=str, help='aligned corpus directory.', required=True)
parser.add_argument('--out-dir', type=str, help='the output directory.', required=True)

if __name__ == '__main__':
    st = time.time()
    args = parser.parse_args()
    src_lang = args.src_lang
    target_lang = args.target_lang
    src_corpus_dir = args.src_corpus
    target_corpus_dir = args.target_corpus
    aligned_dir = args.aligned_corpus
    out_dir = args.out_dir
    main(src_lang, target_lang, src_corpus_dir, target_corpus_dir, aligned_dir, out_dir)
    print("aligner script finished in %s seconds" % (time.time() - st))
