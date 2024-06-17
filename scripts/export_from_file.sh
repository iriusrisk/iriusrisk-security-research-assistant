#!/bin/bash

file="modified.txt"

while IFS= read -r line; do
    if [[ $line == *".yaml" ]]; then
        echo "$line"
        isra component load --file $line
        isra standards expand
        isra component save --format yaml
        isra component batch
    else
        echo "Not a YAML file: $line"
    fi

done < "$file"