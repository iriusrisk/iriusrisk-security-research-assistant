package com.iriusrisk.editor.models.graph;

import lombok.Data;

@Data
public class Link {
    private String source;
    private String target;

    public Link(String source, String target) {
        this.source = source;
        this.target = target;
    }
}
