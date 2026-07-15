#!/bin/bash
set -e

rm -rf sad2021tw/output

tiddlywiki sad2021tw --build static
