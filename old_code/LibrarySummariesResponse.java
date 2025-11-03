package com.iriusrisk.editor.models.graph;

import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class LibrarySummariesResponse {
    private List<LibrarySummary> addedLibraries;
    private List<LibrarySummary> deletedLibraries;
    private List<LibrarySummary> modifiedLibraries;
} 