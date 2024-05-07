#!/bin/bash
directory="/path/to/dir"
# This may be needed if the path came from Windows
# | sed 's/\/mnt\/c/C:/g'
for file in $(find "$directory" -name "*.yaml"); do
    if ! echo "$file" | grep -q "to_review"; then
        echo "$file"
        isra component load --file "$file" > /dev/null
        isra standards expand
        isra component save --format yaml
        isra component batch
    fi
done