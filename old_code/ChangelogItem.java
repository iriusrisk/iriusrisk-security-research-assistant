package com.iriusrisk.editor.models.graph;

import java.util.ArrayList;
import java.util.List;

import lombok.Data;

@Data
public class ChangelogItem {
    private String element;
    private String elementRef;
    private String action;
    private String info;
    private List<Change> changes;

    public ChangelogItem() {
        changes = new ArrayList<>();
    }

    public String toString() {
        return this.info;
    }

}
