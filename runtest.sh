#!/bin/sh

for t in $(ls examples/*_test.py); do
	pytest $t -s;
	[ "$?" -eq 1 ] && exit 1;
done
exit 0;
