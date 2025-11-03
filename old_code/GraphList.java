package com.iriusrisk.editor.models.graph;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import lombok.Data;

@Data
public class GraphList {
    private HashMap<String, Graph> graphs;
    private List<String> addedLibraries;
    private List<String> deletedLibraries;

    public GraphList() {
        graphs = new HashMap<>();
        addedLibraries = new ArrayList<>();
        deletedLibraries = new ArrayList<>();
    }
}
