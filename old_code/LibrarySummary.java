package com.iriusrisk.editor.models.graph;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class LibrarySummary {
    private String libraryRef;
    private String libraryName;
    private String changeType; // "ADDED", "DELETED", "MODIFIED"
    private String oldRevision;
    private String newRevision;
    private boolean hasChanges;
} 