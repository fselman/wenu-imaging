# mefpp CMake frontend: this file contains no native build graph.
.PHONY: all install check test clean help
all:
	@./mefpp2/cmake/frontend.sh build
install: all
	@./mefpp2/cmake/frontend.sh install
check test:
	@./mefpp2/cmake/frontend.sh check
clean:
	@./mefpp2/cmake/frontend.sh clean
help:
	@./mefpp2/cmake/frontend.sh help
