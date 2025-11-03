package com.iriusrisk.editor.models.graph;

import com.iriusrisk.editor.models.elements.IRExtendedRelation;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import lombok.Data;
import lombok.ToString;

@Data
@ToString
public class ChangelogReport {
    public Set<IRExtendedRelation> added;
    public Set<IRExtendedRelation> deleted;
    public HashMap<String, List<IRExtendedRelation>> newCountermeasures;

    public ChangelogReport(){
        added = new HashSet<>();
        deleted = new HashSet<>();
        newCountermeasures = new HashMap<>();
    }



}
