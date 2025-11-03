package com.iriusrisk.editor.models.graph;

import lombok.Data;

@Data
public class Change {
    private String field;
    private String old;
    private String neww;

    public Change(String field, String old, String neww) {
        this.field = field;
        this.old = old;
        this.neww = neww;
    }

    public String toString() {
        return "Field: [" + field + "] Old value: [" + old + "] New value [" + neww + "]";
    }
}
