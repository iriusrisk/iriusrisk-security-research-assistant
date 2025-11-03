package com.iriusrisk.editor.models.graph;

import java.util.ArrayList;
import java.util.List;

import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
public class IRNode extends Node {
    private String name;
    private List<Change> changes;
    private String type;
    private String color;

    public IRNode(String name, String type) {
        super();
        this.name = name;
        this.changes = new ArrayList<>();
        this.type = type;
        setColorFromType();
    }

    public IRNode(String name, List<Change> changes, String type) {
        super();
        this.name = name;
        this.changes = changes;
        this.type = type;
        setColorFromType();
    }

    private void setColorFromType() {
        switch (type) {
            case "E":
                this.color = "#f6ec48";
                break;
            case "N":
                this.color = "#39e260";
                break;
            case "D":
                this.color = "#fa4040";
                break;
            case "ROOT":
                this.color = "#30cbe8";
                break;
            default:
                this.color = "#C0C0C0";
        }
    }

    public void setType(String type) {
        this.type = type;
        setColorFromType();
    }

    public String toString() {
        return "[ " + this.getId() + " / " + this.name + " ]";
    }
}
