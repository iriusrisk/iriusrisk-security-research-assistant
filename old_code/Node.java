package com.iriusrisk.editor.models.graph;

import java.util.UUID;

import lombok.Data;

@Data
public class Node {
    private String id;

    public Node(){
        this.id = UUID.randomUUID().toString();
    }
}
