package com.iriusrisk.editor.models.graph;

import com.iriusrisk.editor.configuration.PropertiesManager;

import java.util.ArrayList;
import java.util.List;

import lombok.Data;

@Data
public class Graph {
    private boolean directed;
    private boolean multigraph;
    private boolean showMitigations;
    private String revFirst;
    private String revSecond;
    private boolean equalRevisionNumber;
    private List<Node> nodes;
    private List<Link> links;
    private List<ChangelogItem> changelogList;

    public Graph() {
        directed = true;
        multigraph = false;
        revFirst = "";
        revSecond = "";
        equalRevisionNumber = false;
        nodes = new ArrayList<>();
        links = new ArrayList<>();
        changelogList = new ArrayList<>();
        showMitigations = false;

        String showMitigationsProp = PropertiesManager.getProperty("show-mitigation-values-on-changelog");
        if (showMitigationsProp != null) {
            showMitigations = Boolean.parseBoolean(showMitigationsProp);
        }
    }

    public boolean hasNodeValue(String id) {
        return nodes.stream().anyMatch(x -> x.getId().equals(id));
    }
}
