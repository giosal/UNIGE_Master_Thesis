import argparse
import sys
import parse_sql_script
import os
import worker
import time
from bs4 import BeautifulSoup

def get_target_title(df, doc_id, ll_lang):
    try:
        title = df.loc[(df.ll_from == doc_id) & (df.ll_lang == ll_lang), 'll_title'].values[0]
        return title
    except IndexError as error:
        return None


def get_doc_by_title(title, corpus):
    for wiki_doc in corpus:
        doc_id, doc_title, doc = wiki_doc
        if doc_title == title:
            return wiki_doc
    return None


def write_file(f, doc):
    doc_id, title, d = doc
    with open(f, 'w') as file_writer:
        strr = [str(doc_id), str(title), str(d)]
        file_writer.write(', '.join(strr))
        file_writer.close()


def save_docs(src_doc, target_doc, src_lang, target_lang, out_dir, file_count):
    src_path = os.path.join(out_dir, src_lang)
    target_path = os.path.join(out_dir, target_lang)
    file_name = "file_{:06d}.txt".format(file_count)
    src_out = os.path.join(src_path, file_name)
    target_out = os.path.join(target_path, file_name)
    write_file(src_out, src_doc)
    write_file(target_out, target_doc)

def do_work(src_lang, target_lang, src_df, src_corpus, target_corpus, out_dir):
    print("aligning documents ...")
    print("source corpus size: {0} documents".format(len(src_corpus)))
    aligned_count = 0
    processed_count = 0
    for src_doc in src_corpus:
        doc_id, title, doc = src_doc
        target_title = get_target_title(src_df, doc_id, target_lang)
        if target_title:
            target_doc = get_doc_by_title(target_title, target_corpus)
            if target_doc:
                save_docs(src_doc, target_doc, src_lang, target_lang, out_dir, aligned_count)
                aligned_count += 1
        sys.stdout.write("\rdocuments processed: {0}\t\tdocuments aligned: {1}".format(processed_count, aligned_count))
        sys.stdout.flush()
        processed_count += 1
    print("\nwriting aligned documents completed successfully!")
    
def load_corpus(corpus_dir):
    st = time.time()
    corpus = list()
    for subdir, dirs, files in sorted(os.walk(corpus_dir)):
        print("subdir: " + subdir)
        for f in files:
            wiki_file = os.path.join(subdir, f)
            with open(wiki_file, encoding='utf-8') as wiki_reader:
                text = wiki_reader.read()
                soup = BeautifulSoup(text, 'html.parser')
                docs = soup.find_all('doc')
                targ = corpus_dir + "corpus.txt"
                g = open(targ, 'w', encoding='utf-8')
                for doc in docs:
                    doc_id = doc.get('id')
                    title = doc.get('title')
                    g.write(str((doc_id, title, wiki_file)))
                    corpus.append((doc_id, title, wiki_file))
                g.close()
                wiki_reader.close()
    print("reading corpus completed successfully in %s seconds" % (time.time() - st))
    return corpus

def main(src_lang, target_lang, src_ll_sql, src_corpus_dir, target_corpus_dir, out_dir):
    start_time = time.time()
    print('source language:', src_lang)
    print('target language:', target_lang)
    print('source language links sql file', src_ll_sql)
    print('source corpus directory', src_corpus_dir)
    print('target corpus directory', target_corpus_dir)
    print('output directory', out_dir)

    src_path = os.path.join(out_dir, src_lang)
    target_path = os.path.join(out_dir, target_lang)
    if not os.path.exists(src_path): os.makedirs(src_path)
    if not os.path.exists(target_path): os.makedirs(target_path)

    src_df = parse_sql_script.sql2df(src_ll_sql, target_lang)

    print("inter-language links sql file loaded successfully")

    src_corpus = load_corpus(src_corpus_dir)
    target_corpus = load_corpus(target_corpus_dir)
    print("source and target corpus loaded successfully")
    do_work(src_lang, target_lang, src_df, src_corpus, target_corpus, out_dir)

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
parser.add_argument('--sql-file', type=str, help='source language links sql file. '
                                                'Obtained from https://dumps.wikimedia.org/', required=True)
parser.add_argument('--src-corpus', type=str, help='source corpus directory.', required=True)
parser.add_argument('--target-corpus', type=str, help='target corpus directory.', required=True)
parser.add_argument('--out-dir', type=str, help='the output directory.', required=True)

if __name__ == '__main__':
    st = time.time()
    args = parser.parse_args()
    src_lang = args.src_lang
    target_lang = args.target_lang
    src_ll_sql = args.sql_file
    src_corpus_dir = args.src_corpus
    target_corpus_dir = args.target_corpus
    out_dir = args.out_dir
    main(src_lang, target_lang, src_ll_sql, src_corpus_dir, target_corpus_dir, out_dir)
    print("aligner script finished in %s seconds" % (time.time() - st))

'''

python aligner.py ar arz /home/motaz/back09022017/wiki/arwiki-20170120-langlinks.sql /home/motaz/back09022017/wiki/arwiki /home/motaz/back09022017/wiki/arzwiki /home/motaz/tmp/out/

'''
