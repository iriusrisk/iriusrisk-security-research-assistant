#!/bin/bash

file="modified.txt"

while IFS= read -r line; do
    echo "$line"
    isra component load --file $line
    isra standards expand
    isra component save --format yaml
    isra component batch
done < "$file"