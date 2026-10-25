# mefpp CMake frontend: this file contains no native build graph.
.PHONY: all install check test clean help
all:
	@./cmake/frontend.sh build
install: all
	@./cmake/frontend.sh install
check test:
	@./cmake/frontend.sh check
clean:
	@./cmake/frontend.sh clean
help:
	@./cmake/frontend.sh help
