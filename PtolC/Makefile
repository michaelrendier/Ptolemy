# PtolC/Makefile — C Monad build

CC      = gcc
CFLAGS  = -O2 -Wall -Wextra -std=c11 -D_POSIX_C_SOURCE=200809L
LDFLAGS = -lm

TARGET  = ptolemy
SRCS    = main.c monad.c checkpoint.c tokenizer.c
OBJS    = $(SRCS:.c=.o)

.PHONY: all clean export corpus full expand ingest

all: $(TARGET)

# ── Corpus: download WordNet + ingest → monad_wordnet.bin ───────────────────
# Requires Python 3 + NLTK.  Runs in ~6 seconds.
# Usage: make corpus
corpus: $(TARGET)
	@echo "[corpus] checking NLTK wordnet…"
	@python3 -m nltk.downloader -q wordnet 2>/dev/null || \
	    (pip install --quiet nltk && python3 -m nltk.downloader -q wordnet)
	@echo "[corpus] extracting lemmas + definitions (313K lines)…"
	@python3 tools/dump_wordnet.py | ./$(TARGET) -i -l -
	@echo "[corpus] done → monad_wordnet.bin"

# ── Full: binary + corpus in one step ───────────────────────────────────────
full: $(TARGET) corpus

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

# Export Python checkpoint to binary (run from Ptolemy3/ root)
export:
	python3 ../Callimachus/checkpoint_export.py

# Expand checkpoint zero field — usage: make expand N=255400
expand: tools/checkpoint_expand
	./tools/checkpoint_expand monad_wordnet.bin $(N)

tools/checkpoint_expand: tools/checkpoint_expand.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

# Full system ingest — usage: make ingest  (or: make ingest FIRST=/SystemTree.txt)
FIRST ?= /SystemTree.txt
ingest: $(TARGET)
	python3 tools/ingest_system.py --root / --first $(FIRST)

# Remove build artifacts
clean:
	rm -f $(OBJS) $(TARGET) tools/checkpoint_expand

# ── Dependencies ────────────────────────────────────────────────────────────
main.o:        main.c ptolemy.h monad.h checkpoint.h tokenizer.h
monad.o:       monad.c ptolemy.h monad.h tokenizer.h
checkpoint.o:  checkpoint.c ptolemy.h checkpoint.h monad.h
tokenizer.o:   tokenizer.c tokenizer.h
