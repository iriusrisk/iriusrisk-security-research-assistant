package com.iriusrisk.editor.services;

import com.iriusrisk.editor.models.ILEVersion;
import com.iriusrisk.editor.models.elements.IRCategoryComponent;
import com.iriusrisk.editor.models.elements.IRComponentDefinition;
import com.iriusrisk.editor.models.elements.IRControl;
import com.iriusrisk.editor.models.elements.IRControlItem;
import com.iriusrisk.editor.models.elements.IRExtendedRelation;
import com.iriusrisk.editor.models.elements.IRLibrary;
import com.iriusrisk.editor.models.elements.IRReference;
import com.iriusrisk.editor.models.elements.IRRelation;
import com.iriusrisk.editor.models.elements.IRRiskPattern;
import com.iriusrisk.editor.models.elements.IRRiskPatternItem;
import com.iriusrisk.editor.models.elements.IRRule;
import com.iriusrisk.editor.models.elements.IRStandard;
import com.iriusrisk.editor.models.elements.IRSupportedStandard;
import com.iriusrisk.editor.models.elements.IRThreat;
import com.iriusrisk.editor.models.elements.IRThreatItem;
import com.iriusrisk.editor.models.elements.IRUseCase;
import com.iriusrisk.editor.models.elements.IRUseCaseItem;
import com.iriusrisk.editor.models.elements.IRWeakness;
import com.iriusrisk.editor.models.elements.IRWeaknessItem;
import com.iriusrisk.editor.models.graph.Change;
import com.iriusrisk.editor.models.graph.ChangelogItem;
import com.iriusrisk.editor.models.graph.ChangelogReport;
import com.iriusrisk.editor.models.graph.Graph;
import com.iriusrisk.editor.models.graph.GraphList;
import com.iriusrisk.editor.models.graph.IRNode;
import com.iriusrisk.editor.models.graph.Link;
import com.iriusrisk.editor.models.graph.LibrarySummary;
import com.iriusrisk.editor.models.graph.LibrarySummariesResponse;
import com.iriusrisk.editor.models.request.ChangelogRequest;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.JSONArray;
import org.json.JSONObject;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.stream.Collectors;

import lombok.RequiredArgsConstructor;


@Service
@RequiredArgsConstructor
public class ChangelogService {

    private static final Logger logger = LogManager.getLogger(ChangelogService.class);

    private final DataService dataService;

    private Graph graph;
    private ILEVersion fv;
    private IRLibrary first;
    private ILEVersion sv;
    private IRLibrary second;

    public void setChangelogItems(ChangelogRequest changelogRequest) {
        ILEVersion fv = dataService.getVersion(changelogRequest.getFirstVersion());
        IRLibrary first = null;
        if (changelogRequest.getFirstLibrary() != null) {
            first = dataService.getLibrary(fv.getVersion(), changelogRequest.getFirstLibrary());
        }
        ILEVersion sv = dataService.getVersion(changelogRequest.getSecondVersion());
        IRLibrary second = null;
        if (changelogRequest.getSecondLibrary() != null) {
            second = dataService.getLibrary(sv.getVersion(), changelogRequest.getSecondLibrary());
        }
        this.graph = new Graph();
        this.fv = fv;
        this.first = first;
        this.sv = sv;
        this.second = second;
    }

    public Graph getLibraryChanges() {
        // If the libraries and the versions are the same there is no point to do the changelog
        graph = new Graph();
        if (first.getRef().equals(second.getRef()) && fv.getVersion().equals(sv.getVersion())) {
            return new Graph();
        }
        logger.info("Creating changelog for {}/{} => {}/{}", fv.getVersion(), first.getRef(), sv.getVersion(), second.getRef());

        List<Change> changes = new ArrayList<>();
        getChange(changes, "revision", first.getRevision(), second.getRevision());
        getChange(changes, "ref", first.getRef(), second.getRef());
        getChange(changes, "name", first.getName(), second.getName());
        getChange(changes, "desc", first.getDesc(), second.getDesc());
        getChange(changes, "filename", first.getFilename(), second.getFilename());
        getChange(changes, "enabled", first.getEnabled(), second.getEnabled());

        // Root node, always appears
        IRNode root = new IRNode(second.getRef(), changes, "ROOT");
        if (!changes.isEmpty()) {
            root.setType("E");
            addItemToChangelogList("Library", second.getRef(), "E", changes);
        }
        graph.getNodes().add(root);

        // Category components
        addCategoriesToGraph(root.getId());

        // Component definitions
        addComponentsToGraph(root.getId());

        // Supported Standards
        addSupportedStandardsToGraph(root.getId());

        // Standards
        addStandardsToGraph(root.getId());

        // Risk patterns
        addRiskPatternsToGraph(root.getId());

        // Rules
        addRulesToGraph(root.getId());

        // If we are checking libraries from the same version we don't have to check for differences between
        // some nodes.
        if (!fv.getVersion().equals(sv.getVersion())) {
            // Usecases
            addUsecasesToGraph(root.getId());
            // Threats
            addThreatsToGraph(root.getId());
            // Controls
            addControlsToGraph(root.getId());
            // Weaknesses
            addWeaknessesToGraph(root.getId());
            // References
            addReferencesToGraph(root.getId());
        }

        graph.setRevFirst(first.getRevision());
        graph.setRevSecond(second.getRevision());

        if (!graph.getChangelogList().isEmpty() && first.getRevision().equals(second.getRevision())) {
            logger.info("This library has the same revision number but it has changes");
            graph.setEqualRevisionNumber(true);
        }

        return graph;
    }

    public GraphList getVersionChanges() {
        GraphList gl = new GraphList();
        for (String l1 : fv.getLibraries().keySet()) {
            if (sv.getLibraries().containsKey(l1)) {
                this.first = fv.getLibrary(l1);
                this.second = sv.getLibrary(l1);
                gl.getGraphs().put(l1, getLibraryChanges());
            } else {
                gl.getDeletedLibraries().add(fv.getLibrary(l1).getName());
            }
        }

        for (String l2 : sv.getLibraries().keySet()) {
            if (!fv.getLibraries().containsKey(l2)) {
                gl.getAddedLibraries().add(sv.getLibrary(l2).getName());
            }
        }

        return gl;
    }

    private boolean addUsecasesToGraph(String parentId) {
        List<IRNode> nodeList = new ArrayList<>();

        Set<String> usecaseFirst = getListFromRelations(first, "usecases");
        Set<String> usecaseSecond = getListFromRelations(second, "usecases");

        for (String uc1 : usecaseFirst) {
            if (usecaseSecond.contains(uc1)) {
                IRUseCase u1 = fv.getUsecases().get(uc1);
                IRUseCase u2 = sv.getUsecases().get(uc1);
                List<Change> changes = new ArrayList<>();
                getChange(changes, "name", u1.getName(), u2.getName());
                getChange(changes, "desc", u1.getDesc(), u2.getDesc());

                IRNode node = new IRNode(u2.getRef(), changes, "E");

                if (!changes.isEmpty()) {
                    // Modified
                    addItemToChangelogList("Usecases", node.getName(), "E", changes);
                    nodeList.add(node);
                }
            } else {
                // Deleted
                IRNode node = new IRNode(uc1, new ArrayList<>(), "D");
                addItemToChangelogList("Usecases", node.getName(), "D", new ArrayList<>());
                nodeList.add(node);
            }
        }

        for (String th2 : usecaseSecond) {
            if (!usecaseFirst.contains(th2)) {
                // Added
                IRNode node = new IRNode(th2, new ArrayList<>(), "N");
                addItemToChangelogList("Usecases", node.getName(), "N", new ArrayList<>());
                nodeList.add(node);
            }
        }

        return createIntermediateNode(parentId, "usecases", nodeList);
    }

    private boolean addThreatsToGraph(String parentId) {
        List<IRNode> nodeList = new ArrayList<>();

        Set<String> threatsFirst = getListFromRelations(first, "threats");
        Set<String> threatsSecond = getListFromRelations(second, "threats");

        for (String th1 : threatsFirst) {
            if (threatsSecond.contains(th1)) {
                IRThreat t1 = fv.getThreats().get(th1);
                IRThreat t2 = sv.getThreats().get(th1);
                List<Change> changes = new ArrayList<>();
                getChange(changes, "name", t1.getName(), t2.getName());
                getChange(changes, "desc", t1.getDesc(), t2.getDesc());
                getChange(changes, "confidentiality", t1.getRiskRating().getConfidentiality(), t2.getRiskRating().getConfidentiality());
                getChange(changes, "integrity", t1.getRiskRating().getIntegrity(), t2.getRiskRating().getIntegrity());
                getChange(changes, "availability", t1.getRiskRating().getAvailability(), t2.getRiskRating().getAvailability());
                getChange(changes, "easeOfExploitation", t1.getRiskRating().getEaseOfExploitation(), t2.getRiskRating().getEaseOfExploitation());

                IRNode node = new IRNode(t2.getRef(), changes, "E");

                boolean references = addReferencesToGraph(node.getId(), "Threat:References", "references", t1.getReferences(), t2.getReferences());

                if (!changes.isEmpty() || references
                ) {
                    // Modified
                    addItemToChangelogList("Threats", node.getName(), "E", changes);
                    nodeList.add(node);
                }
            } else {
                // Deleted
                IRNode node = new IRNode(th1, new ArrayList<>(), "D");
                addItemToChangelogList("Threats", node.getName(), "D", new ArrayList<>());
                nodeList.add(node);
            }
        }

        for (String th2 : threatsSecond) {
            if (!threatsFirst.contains(th2)) {
                // Added
                IRNode node = new IRNode(th2, new ArrayList<>(), "N");
                addItemToChangelogList("Threats", node.getName(), "N", new ArrayList<>());
                nodeList.add(node);
            }
        }

        return createIntermediateNode(parentId, "threats", nodeList);
    }

    private boolean addWeaknessesToGraph(String parentId) {
        List<IRNode> nodeList = new ArrayList<>();

        Set<String> weaknessFirst = getListFromRelations(first, "weaknesses");
        Set<String> weaknessSecond = getListFromRelations(second, "weaknesses");

        for (String weakness1 : weaknessFirst) {
            if (weaknessSecond.contains(weakness1)) {
                IRWeakness w1 = fv.getWeaknesses().get(weakness1);
                IRWeakness w2 = sv.getWeaknesses().get(weakness1);
                List<Change> changes = new ArrayList<>();
                getChange(changes, "name", w1.getName(), w2.getName());
                getChange(changes, "desc", w1.getDesc(), w2.getDesc());
                getChange(changes, "impact", w1.getImpact(), w2.getImpact());
                getChange(changes, "steps", w1.getTest().getSteps(), w2.getTest().getSteps());

                IRNode node = new IRNode(w2.getRef(), changes, "E");

                boolean testReferences = addReferencesToGraph(node.getId(), "Weaknesses:TestReferences", "testReferences", w1.getTest().getReferences(), w2.getTest().getReferences());

                if (!changes.isEmpty() || testReferences
                ) {
                    // Modified
                    addItemToChangelogList("Weaknesses", node.getName(), "E", changes);
                    nodeList.add(node);
                }
            } else {
                // Deleted
                IRNode node = new IRNode(weakness1, new ArrayList<>(), "D");
                addItemToChangelogList("Weaknesses", node.getName(), "D", new ArrayList<>());
                nodeList.add(node);
            }
        }

        for (String w2 : weaknessSecond) {
            if (!weaknessFirst.contains(w2)) {
                // Added
                IRNode node = new IRNode(w2, new ArrayList<>(), "N");
                addItemToChangelogList("Weaknesses", node.getName(), "N", new ArrayList<>());
                nodeList.add(node);
            }
        }

        return createIntermediateNode(parentId, "weaknesses", nodeList);
    }

    private boolean addControlsToGraph(String parentId) {
        List<IRNode> nodeList = new ArrayList<>();

        Set<String> controlFirst = getListFromRelations(first, "controls");
        Set<String> controlSecond = getListFromRelations(second, "controls");

        for (String control1 : controlFirst) {
            if (controlSecond.contains(control1)) {
                IRControl c1 = fv.getControls().get(control1);
                IRControl c2 = sv.getControls().get(control1);
                List<Change> changes = new ArrayList<>();
                getChange(changes, "name", c1.getName(), c2.getName());
                getChange(changes, "desc", c1.getDesc(), c2.getDesc());
                getChange(changes, "state", c1.getState(), c2.getState());
                getChange(changes, "cost", c1.getCost(), c2.getCost());
                getChange(changes, "steps", c1.getTest().getSteps(), c2.getTest().getSteps());

                IRNode node = new IRNode(c2.getRef(), changes, "E");

                boolean standards = addStandardsToGraph(node.getId(), "Controls:Standards", "standards", c1.getStandards(), c2.getStandards());
                boolean references = addReferencesToGraph(node.getId(), "Controls:References", "references", c1.getReferences(), c2.getReferences());
                boolean testReferences = addReferencesToGraph(node.getId(), "Controls:TestReferences", "testReferences", c1.getTest().getReferences(), c2.getTest().getReferences());
                boolean implementations = addImplementationsToGraph(node.getId(), "Controls:Implementations", "implementations", c1.getImplementations(), c2.getImplementations());

                if (!changes.isEmpty() || references || testReferences || standards
                ) {
                    // Modified
                    addItemToChangelogList("Controls", node.getName(), "E", changes);
                    nodeList.add(node);
                }
            } else {
                // Deleted
                IRNode node = new IRNode(control1, new ArrayList<>(), "D");
                addItemToChangelogList("Controls", node.getName(), "D", new ArrayList<>());
                nodeList.add(node);
            }
        }

        for (String w2 : controlSecond) {
            if (!controlFirst.contains(w2)) {
                // Added
                IRNode node = new IRNode(w2, new ArrayList<>(), "N");
                addItemToChangelogList("Controls", node.getName(), "N", new ArrayList<>());
                nodeList.add(node);
            }
        }

        return createIntermediateNode(parentId, "controls", nodeList);
    }

    private boolean addStandardsToGraph(String parentId) {
        List<IRNode> nodeList = new ArrayList<>();

        Collection<IRStandard> standardsInFirstLibrary = fv.getStandards().values();
        Collection<IRStandard> standardsInSecondLibrary = sv.getStandards().values();

        for (IRStandard st : standardsInFirstLibrary) {
            Optional<IRStandard> standardOptional = standardsInSecondLibrary.stream()
                    .filter(x->x.getStandardRef().equals(st.getStandardRef()) && x.getSupportedStandardRef().equals(st.getSupportedStandardRef())).findFirst();
            if(!standardOptional.isPresent()){
                // Deleted
                IRNode sNode = new IRNode(st.getSupportedStandardRef()+"-"+st.getStandardRef(), new ArrayList<>(), "D");
                addItemToChangelogList("Standards", sNode.getName(), "D", new ArrayList<>());
                nodeList.add(sNode);
            }
        }

        for (IRStandard st : standardsInSecondLibrary) {
            Optional<IRStandard> standardOptional = standardsInFirstLibrary.stream()
                    .filter(x->x.getStandardRef().equals(st.getStandardRef()) && x.getSupportedStandardRef().equals(st.getSupportedStandardRef())).findFirst();

            if (!standardOptional.isPresent()) {
                // Added
                IRNode sNode = new IRNode(st.getSupportedStandardRef()+"-"+st.getStandardRef(), new ArrayList<>(), "N");
                addItemToChangelogList("Standards", sNode.getName(), "N", new ArrayList<>());
                nodeList.add(sNode);
            }
        }

        return createIntermediateNode(parentId, "standards", nodeList);
    }


    private boolean addStandardsToGraph(String parentId, String element, String intermediate, TreeMap<String, String> standards1, TreeMap<String, String> standards2) {
        List<IRNode> nodeList = new ArrayList<>();

        Set<String> standardsFirst = standards1.entrySet().stream().map(x -> x.getKey()).collect(Collectors.toSet());
        Set<String> standardsSecond = standards2.entrySet().stream().map(x -> x.getKey()).collect(Collectors.toSet());

        // Added
        standardsSecond.stream()
                .filter(x -> !standardsFirst.contains(x))
                .map(x -> {
                    nodeList.add(new IRNode(x, new ArrayList<>(), "N"));
                    addItemToChangelogList(element, x, "N", new ArrayList<>());
                    return x;
                }).collect(Collectors.toSet());

        // Deleted
        standardsFirst.stream()
                .filter(x -> !standardsSecond.contains(x))
                .map(x -> {
                    nodeList.add(new IRNode(x, new ArrayList<>(), "D"));
                    addItemToChangelogList(element, x, "D", new ArrayList<>());
                    return x;
                }).collect(Collectors.toSet());

        if (!"".equals(intermediate)) {
            return createIntermediateNode(parentId, intermediate, nodeList);
        } else {
            return addNodesToGraph(parentId, nodeList);
        }
    }

    private boolean addImplementationsToGraph(String parentId, String element, String intermediate, Set<String> impl1, Set<String> impl2) {
        List<IRNode> nodeList = new ArrayList<>();

        // Added
        impl2.stream()
                .filter(x -> !impl1.contains(x))
                .map(x -> {
                    nodeList.add(new IRNode(x, new ArrayList<>(), "N"));
                    addItemToChangelogList(element, x, "N", new ArrayList<>());
                    return x;
                }).collect(Collectors.toSet());

        // Deleted
        impl1.stream()
                .filter(x -> !impl2.contains(x))
                .map(x -> {
                    nodeList.add(new IRNode(x, new ArrayList<>(), "D"));
                    addItemToChangelogList(element, x, "D", new ArrayList<>());
                    return x;
                }).collect(Collectors.toSet());

        if (!"".equals(intermediate)) {
            return createIntermediateNode(parentId, intermediate, nodeList);
        } else {
            return addNodesToGraph(parentId, nodeList);
        }
    }

    private boolean addReferencesToGraph(String parentId) {
        List<IRNode> nodeList = new ArrayList<>();

        Set<IRReference> referencesFirst = new TreeSet<>();
        for(IRRelation rel: first.getRelations().values()){
            if(rel.getThreatUuid()!=null){
                for(String s : fv.getThreats().get(rel.getThreatUuid()).getReferences().values()){
                    referencesFirst.add(fv.getReferences().get(s));
                }
            }
            if(rel.getWeaknessUuid()!=null){
                for(String s : fv.getWeaknesses().get(rel.getWeaknessUuid()).getTest().getReferences().values()){
                    referencesFirst.add(fv.getReferences().get(s));
                }
            }
            if(rel.getControlUuid()!=null){
                for(String s : fv.getControls().get(rel.getControlUuid()).getReferences().values()){
                    referencesFirst.add(fv.getReferences().get(s));
                }
                for(String s : fv.getControls().get(rel.getControlUuid()).getTest().getReferences().values()){
                    referencesFirst.add(fv.getReferences().get(s));
                }
            }
        }

        Set<IRReference> referencesSecond = new TreeSet<>();
        for(IRRelation rel: second.getRelations().values()){
            if(rel.getThreatUuid()!=null){
                for(String s : sv.getThreats().get(rel.getThreatUuid()).getReferences().values()){
                    referencesSecond.add(sv.getReferences().get(s));
                }
            }
            if(rel.getWeaknessUuid()!=null){
                for(String s : sv.getWeaknesses().get(rel.getWeaknessUuid()).getTest().getReferences().values()){
                    referencesSecond.add(sv.getReferences().get(s));
                }
            }
            if(rel.getControlUuid()!=null){
                for(String s : sv.getControls().get(rel.getControlUuid()).getReferences().values()){
                    referencesSecond.add(sv.getReferences().get(s));
                }
                for(String s : sv.getControls().get(rel.getControlUuid()).getTest().getReferences().values()){
                    referencesSecond.add(sv.getReferences().get(s));
                }
            }
        }

        for (IRReference ref1 : referencesFirst) {
            Optional<IRReference> referenceOptional = referencesSecond.stream().filter(x->x.getName().equals(ref1.getName())).findFirst();

            if (referenceOptional.isPresent()) {
                // Modified references
                List<Change> changes = new ArrayList<>();
                String url1 = ref1.getUrl();
                String url2 = referenceOptional.get().getUrl();

                getChange(changes, "url", url1, url2);

                if (!changes.isEmpty()) {
                    IRNode node = new IRNode(ref1.getName(), changes, "E");
                    addItemToChangelogList("References", node.getName(), "E", changes);
                    nodeList.add(node);
                }
            } else {
                // Deleted
                IRNode node = new IRNode(ref1.getName(), new ArrayList<>(), "D");
                addItemToChangelogList("References", node.getName(), "D", new ArrayList<>());
                nodeList.add(node);
            }
        }

        for (IRReference ref2 : referencesSecond) {
            Optional<IRReference> referenceOptional = referencesFirst.stream().filter(x->x.getName().equals(ref2.getName())).findFirst();

            if (!referenceOptional.isPresent()) {
                // Added references
                IRNode node = new IRNode(ref2.getName(), new ArrayList<>(), "N");
                addItemToChangelogList("References", node.getName(), "N", new ArrayList<>());
                nodeList.add(node);
            }
        }


        return createIntermediateNode(parentId, "references", nodeList);
    }

    private boolean addReferencesToGraph(String parentId, String element, String intermediate, TreeMap<String, String> references1, TreeMap<String, String> references2) {
        List<IRNode> nodeList = new ArrayList<>();

        // Added
        Set<String> referencesOne = references1.entrySet().stream().map(x -> x.getKey()).collect(Collectors.toSet());
        Set<String> referencesTwo = references2.entrySet().stream().map(x -> x.getKey()).collect(Collectors.toSet());

        referencesTwo.stream()
                .filter(x -> !referencesOne.contains(x))
                .map(x -> {
                    nodeList.add(new IRNode(x, new ArrayList<>(), "N"));
                    addItemToChangelogList(element, x, "N", new ArrayList<>());
                    return x;
                }).collect(Collectors.toSet());

        // Deleted
        referencesOne.stream()
                .filter(x -> !referencesTwo.contains(x))
                .map(x -> {
                    nodeList.add(new IRNode(x, new ArrayList<>(), "D"));
                    addItemToChangelogList(element, x, "D", new ArrayList<>());
                    return x;
                }).collect(Collectors.toSet());


        if (!"".equals(intermediate)) {
            return createIntermediateNode(parentId, intermediate, nodeList);
        } else {
            return addNodesToGraph(parentId, nodeList);
        }
    }

    private boolean addCategoriesToGraph(String parentId) {
        List<IRNode> nodeList = new ArrayList<>();

        Set<String> catFirst = getCategoriesOfComponents(first, fv);
        Set<String> catSecond = getCategoriesOfComponents(second, sv);

        for (String cat1 : catFirst) {
            if (catSecond.contains(cat1)) {
                IRCategoryComponent c1 = fv.getCategories().get(cat1);
                IRCategoryComponent c2 = sv.getCategories().get(cat1);
                List<Change> changes = new ArrayList<>();
                getChange(changes, "name", c1.getName(), c2.getName());
                if (!changes.isEmpty()) {
                    // Modified
                    IRNode cNode = new IRNode(c2.getRef(), changes, "E");
                    addItemToChangelogList("Categories", cNode.getName(), "E", changes);
                    nodeList.add(cNode);
                }
            } else {
                // Deleted
                IRNode cNode = new IRNode(cat1, new ArrayList<>(), "D");
                addItemToChangelogList("Categories", cNode.getName(), "D", new ArrayList<>());
                nodeList.add(cNode);
            }
        }

        for (String cat2 : catSecond) {
            if (!catFirst.contains(cat2)) {
                // Added
                IRNode cNode = new IRNode(cat2, new ArrayList<>(), "N");
                addItemToChangelogList("Categories", cNode.getName(), "N", new ArrayList<>());
                nodeList.add(cNode);
            }
        }

        return createIntermediateNode(parentId, "categories", nodeList);
    }

    private boolean addComponentsToGraph(String parentId) {
        List<IRNode> nodeList = new ArrayList<>();

        // Added
        Set<String> componentsFirst = first.getComponentDefinitions().values().stream().map(x -> x.getRef()).collect(Collectors.toSet());
        second.getComponentDefinitions().values().stream()
                .filter(x -> !componentsFirst.contains(x.getRef()))
                .map(x -> {
                    nodeList.add(new IRNode(x.getRef(), new ArrayList<>(), "N"));
                    addItemToChangelogList("Component Definitions", x.getRef(), "N", new ArrayList<>());
                    return x;
                }).collect(Collectors.toSet());

        // Deleted
        Set<String> componentsSecond = second.getComponentDefinitions().values().stream().map(x -> x.getRef()).collect(Collectors.toSet());
        first.getComponentDefinitions().values().stream()
                .filter(x -> !componentsSecond.contains(x.getRef()))
                .map(x -> {
                    nodeList.add(new IRNode(x.getRef(), new ArrayList<>(), "D"));
                    addItemToChangelogList("Component Definitions", x.getRef(), "D", new ArrayList<>());
                    return x;
                }).collect(Collectors.toSet());

        // Modified
        for (IRComponentDefinition c1 : first.getComponentDefinitions().values()) {
            for (IRComponentDefinition c2 : second.getComponentDefinitions().values()) {
                if (c1.getRef().equals(c2.getRef())) {

                    List<Change> changes = new ArrayList<>();
                    getChange(changes, "name", c1.getName(), c2.getName());
                    getChange(changes, "desc", c1.getDesc(), c2.getDesc());
                    getChange(changes, "categoryRef", c1.getCategoryRef(), c2.getCategoryRef());
                    getChange(changes, "riskPatterns", String.join(",", c1.getRiskPatternRefs()), String.join(",", c2.getRiskPatternRefs()));
                    getChange(changes, "visible", c1.getVisible(), c2.getVisible());

                    if (!changes.isEmpty()) {
                        IRNode cNode = new IRNode(c2.getRef(), changes, "E");
                        addItemToChangelogList("Component Definitions", cNode.getName(), "E", changes);
                        nodeList.add(cNode);
                    }

                    break;
                }

            }
        }

        return createIntermediateNode(parentId, "components", nodeList);
    }

    private boolean addSupportedStandardsToGraph(String parentId) {
        List<IRNode> nodeList = new ArrayList<>();

        TreeMap<String, IRSupportedStandard> standardsInFirstLibrary = fv.getSupportedStandards();
        TreeMap<String, IRSupportedStandard> standardsInSecondLibrary = sv.getSupportedStandards();

        for (Map.Entry<String, IRSupportedStandard> st : standardsInFirstLibrary.entrySet()) {
            if (standardsInSecondLibrary.containsKey(st.getKey())) {
                List<Change> changes = new ArrayList<>();
                getChange(changes, "name", st.getValue().getSupportedStandardName(), standardsInSecondLibrary.get(st.getKey()).getSupportedStandardName());
                if (!changes.isEmpty()) {
                    // Modified
                    IRNode sNode = new IRNode(st.getKey(), changes, "E");
                    addItemToChangelogList("Supported Standards", sNode.getName(), "E", changes);
                    nodeList.add(sNode);
                }
            } else {
                // Deleted
                IRNode sNode = new IRNode(st.getKey(), new ArrayList<>(), "D");
                addItemToChangelogList("Supported Standards", sNode.getName(), "D", new ArrayList<>());
                nodeList.add(sNode);
            }
        }

        for (Map.Entry<String, IRSupportedStandard> st : standardsInSecondLibrary.entrySet()) {
            if (!standardsInFirstLibrary.containsKey(st.getKey())) {
                // Added
                IRNode sNode = new IRNode(st.getKey(), new ArrayList<>(), "N");
                addItemToChangelogList("Supported Standards", sNode.getName(), "N", new ArrayList<>());
                nodeList.add(sNode);
            }
        }

        return createIntermediateNode(parentId, "supported_standards", nodeList);
    }

    private boolean addRiskPatternsToGraph(String parentId) {
        List<IRNode> nodeList = new ArrayList<>();

        for (Map.Entry<String, IRRiskPattern> rpEntry : first.getRiskPatterns().entrySet()) {
            if (second.getRiskPatterns().containsKey(rpEntry.getKey())) {
                IRRiskPattern rp = rpEntry.getValue();
                IRRiskPattern rp2 = second.getRiskPatterns().get(rpEntry.getKey());
                List<Change> changes = new ArrayList<>();
                getChange(changes, "name", rp.getName(), rp2.getName());
                getChange(changes, "desc", rp.getDesc(), rp2.getDesc());
                getChange(changes, "uuid", rp.getUuid(), rp2.getUuid());
                IRNode n = new IRNode(rp2.getRef(), changes, "E");
                boolean changed = addUseCasesToGraph(n.getId(), rp, rp2);

                if (!changes.isEmpty() || changed) {
                    addItemToChangelogList("RiskPattern", rp2.getRef(), "E", changes);
                    nodeList.add(n);
                }
            } else {
                // Deleted
                IRNode node = new IRNode(rpEntry.getKey(), new ArrayList<>(), "D");
                addItemToChangelogList("RiskPattern", node.getName(), "D", new ArrayList<>());
                nodeList.add(node);
            }
        }

        for (Map.Entry<String, IRRiskPattern> st : second.getRiskPatterns().entrySet()) {
            if (!first.getRiskPatterns().containsKey(st.getKey())) {
                // Added
                IRNode node = new IRNode(st.getKey(), new ArrayList<>(), "N");
                addItemToChangelogList("RiskPattern", node.getName(), "N", new ArrayList<>());
                nodeList.add(node);
            }
        }

        return createIntermediateNode(parentId, "riskPatterns", nodeList);
    }

    private boolean addUseCasesToGraph(String parentId, IRRiskPattern rpFirst, IRRiskPattern rpSecond) {
        List<IRNode> nodeList = new ArrayList<>();

        HashMap<String, IRRiskPatternItem> riskPatternTree1 = dataService.getRelationsInTree(first);
        HashMap<String, IRRiskPatternItem> riskPatternTree2 = dataService.getRelationsInTree(second);

        IRRiskPatternItem rpItem1 = riskPatternTree1.get(rpFirst.getRef());
        IRRiskPatternItem rpItem2 = riskPatternTree2.get(rpSecond.getRef());

        if (rpItem1 != null && rpItem2 != null) {
            for (Map.Entry<String, IRUseCaseItem> usecaseRef1 : rpItem1.getUsecases().entrySet()) {
                // ...if the second tree has the item...
                if (rpItem2.getUsecases().containsKey(usecaseRef1.getKey())) {
                    // Modified threats
                    IRUseCaseItem ucItem1 = usecaseRef1.getValue();
                    IRUseCaseItem ucItem2 = rpItem2.getUsecases().get(usecaseRef1.getKey());

                    IRNode n = new IRNode(usecaseRef1.getKey(), new ArrayList<>(), "E");
                    String usecaseId = n.getId();
                    // Threats
                    boolean t = addThreatRelationsToGraph(usecaseId, ucItem1, ucItem2);

                    if (t) {
                        addItemToChangelogList("Relation:Threat", ucItem2.getRef(), "E", new ArrayList<>());
                        nodeList.add(n);
                    }
                }
            }
        }

        return addNodesToGraph(parentId, nodeList);
    }

    private boolean addThreatRelationsToGraph(String parentId, IRUseCaseItem uc1, IRUseCaseItem uc2) {
        List<IRNode> nodeList = new ArrayList<>();

        // First we create the tree structure of the relations
        // Threat has weaknesses and orphaned controls
        // The weaknesses have controls
        // The controls have mitigation values
        HashMap<String, IRThreatItem> th1 = uc1.getThreats();
        HashMap<String, IRThreatItem> th2 = uc2.getThreats();

        // For every threat in the first tree...
        for (Map.Entry<String, IRThreatItem> threatRef1 : th1.entrySet()) {
            // ...if the second tree has the item...
            if (th2.containsKey(threatRef1.getKey())) {
                // Modified threats
                IRThreatItem tItem1 = threatRef1.getValue();
                IRThreatItem tItem2 = th2.get(threatRef1.getKey());

                IRNode n = new IRNode(threatRef1.getKey(), new ArrayList<>(), "E");
                String threatId = n.getId();
                // Weaknesses
                boolean w = addWeaknessRelationsToGraph(threatId, tItem1.getWeaknesses(), tItem2.getWeaknesses());

                // Orphaned Controls
                boolean oc = addControlRelationsToGraph(threatId, tItem1.getOrphanedControls(), tItem2.getOrphanedControls());

                if (w || oc) {
                    addItemToChangelogList("Relation:Threat", tItem2.getRef(), "E", new ArrayList<>());
                    nodeList.add(n);
                }
            } else {
                // If the node is not in the second tree its because it has been deleted
                IRNode tNode = new IRNode(threatRef1.getKey(), new ArrayList<>(), "D");
                addItemToChangelogList("Relation:Threat", tNode.getName(), "D", new ArrayList<>());
                nodeList.add(tNode);
            }
        }

        for (Map.Entry<String, IRThreatItem> t2 : th2.entrySet()) {
            // For every threat in the second tree if the threat is not in the first tree
            // is because the node is new
            if (!th1.containsKey(t2.getKey())) {
                IRNode tNode = new IRNode(t2.getKey(), new ArrayList<>(), "N");
                addItemToChangelogList("Relation:Threat", tNode.getName(), "N", new ArrayList<>());
                nodeList.add(tNode);
            }
        }

        return addNodesToGraph(parentId, nodeList);
    }

    private boolean addWeaknessRelationsToGraph(String parentId, HashMap<String, IRWeaknessItem> weaknesses1, HashMap<String, IRWeaknessItem> weaknesses2) {
        List<IRNode> nodeList = new ArrayList<>();

        for (Map.Entry<String, IRWeaknessItem> weakness1 : weaknesses1.entrySet()) {
            if (weaknesses2.containsKey(weakness1.getKey())) {
                // Modified weakness
                IRWeaknessItem w1 = weakness1.getValue();
                IRWeaknessItem w2 = weaknesses2.get(weakness1.getKey());

                IRNode wNode = new IRNode(w2.getRef(), new ArrayList<>(), "E");
                String weaknessId = wNode.getId();

                // Controls
                boolean weaknessChanged = addControlRelationsToGraph(weaknessId, w1.getControls(), w2.getControls());

                if (weaknessChanged) {
                    addItemToChangelogList("Relation:Weakness", w2.getRef(), "E", new ArrayList<>());
                    nodeList.add(wNode);
                }

            } else {
                // Deleted weakness
                IRNode wNode = new IRNode(weakness1.getValue().getRef(), new ArrayList<>(), "D");
                addItemToChangelogList("Relation:Weakness", wNode.getName(), "D", new ArrayList<>());
                nodeList.add(wNode);
            }
        }

        for (Map.Entry<String, IRWeaknessItem> weakness2 : weaknesses2.entrySet()) {
            if (!weaknesses1.containsKey(weakness2.getKey())) {
                // Added weakness
                IRNode wNode = new IRNode(weakness2.getValue().getRef(), new ArrayList<>(), "N");
                addItemToChangelogList("Relation:Weakness", wNode.getName(), "N", new ArrayList<>());
                nodeList.add(wNode);
            }
        }

        return addNodesToGraph(parentId, nodeList);
    }

    private boolean addControlRelationsToGraph(String parentId, HashMap<String, IRControlItem> controls1, HashMap<String, IRControlItem> controls2) {
        List<IRNode> nodeList = new ArrayList<>();

        for (Map.Entry<String, IRControlItem> control1 : controls1.entrySet()) {
            if (controls2.containsKey(control1.getKey())) {
                // Modified controls
                IRControlItem c1 = control1.getValue();
                IRControlItem c2 = controls2.get(control1.getKey());

                List<Change> changes = new ArrayList<>();
                getChange(changes, "mitigation", c1.getMitigation(), c2.getMitigation());

                if (!changes.isEmpty()) {
                    if (graph.isShowMitigations()) {
                        IRNode cNode = new IRNode(c2.getRef(), changes, "E");
                        nodeList.add(cNode);
                        addItemToChangelogList("Relation:Control", c2.getRef(), "E", changes);
                    }
                }
            } else {
                // Deleted control from threat
                IRNode cNode = new IRNode(control1.getValue().getRef(), new ArrayList<>(), "D");
                addItemToChangelogList("Relation:Control", cNode.getName(), "D", new ArrayList<>());
                nodeList.add(cNode);
            }
        }

        // If a control doesn't exists in the weakness of the first tree its because is new
        for (Map.Entry<String, IRControlItem> control2 : controls2.entrySet()) {
            if (!controls1.containsKey(control2.getKey())) {
                // Added control to threat
                IRNode cNode = new IRNode(control2.getValue().getRef(), new ArrayList<>(), "N");
                addItemToChangelogList("Relation:Control", cNode.getName(), "N", new ArrayList<>());
                nodeList.add(cNode);
            }
        }

        return addNodesToGraph(parentId, nodeList);

    }

    private boolean addRulesToGraph(String parentId) {
        List<IRNode> nodeList = new ArrayList<>();

        // Added
        Set<String> rulesFirst = first.getRules().stream().map(x -> x.getName()).collect(Collectors.toSet());
        second.getRules().stream()
                .filter(x -> !rulesFirst.contains(x.getName()))
                .map(x -> {
                    nodeList.add(new IRNode(x.getName(), new ArrayList<>(), "N"));
                    addItemToChangelogList("Rules", x.getName(), "N", new ArrayList<>());
                    return x;
                }).collect(Collectors.toSet());

        // Deleted
        Set<String> riskPatternsSecond = second.getRules().stream().map(IRRule::getName).collect(Collectors.toSet());
        first.getRules().stream()
                .filter(x -> !riskPatternsSecond.contains(x.getName()))
                .map(x -> {
                    nodeList.add(new IRNode(x.getName(), new ArrayList<>(), "D"));
                    addItemToChangelogList("Rules", x.getName(), "D", new ArrayList<>());
                    return x;
                }).collect(Collectors.toSet());

        // Modified
        for (IRRule r1 : first.getRules()) {
            for (IRRule r2 : second.getRules()) {
                if (r1.getName().equals(r2.getName())) {
                    List<Change> changes = new ArrayList<>();
                    getChange(changes, "name", r1.getName(), r2.getName());
                    getChange(changes, "module", r1.getModule(), r2.getModule());
                    getChange(changes, "gui", r1.getGui(), r2.getGui());

                    IRNode n = new IRNode(r2.getName(), changes, "E");

                    boolean conditions = addConditionsToRule(n.getId(), r1, r2);
                    boolean actions = addActionsToRule(n.getId(), r1, r2);

                    if (!changes.isEmpty() || conditions || actions) {
                        addItemToChangelogList("Rules", r2.getName(), "E", changes);
                        nodeList.add(n);
                    }

                    break;
                }
            }
        }

        return createIntermediateNode(parentId, "rules", nodeList);
    }

    private boolean addConditionsToRule(String parentId, IRRule r1, IRRule r2) {
        List<IRNode> nodeList = new ArrayList<>();

        Set<String> conditionInString1 = r1.getConditions().stream().map(x -> x.getField() + "####" + x.getName() + "####" + x.getValue()).collect(Collectors.toSet());
        Set<String> conditionInString2 = r2.getConditions().stream().map(x -> x.getField() + "####" + x.getName() + "####" + x.getValue()).collect(Collectors.toSet());

        for (String c1 : conditionInString1) {
            if (!conditionInString2.contains(c1)) {
                String[] split = c1.split("####");
                IRNode cNode = new IRNode(Arrays.toString(split), new ArrayList<>(), "D");
                addItemToChangelogList("Rules", r1.getName() + "[Condition]" + Arrays.toString(split), "D", new ArrayList<>());
                nodeList.add(cNode);
            }
        }

        for (String c2 : conditionInString2) {
            if (!conditionInString1.contains(c2)) {
                String[] split = c2.split("####");
                IRNode cNode = new IRNode(Arrays.toString(split), new ArrayList<>(), "N");
                addItemToChangelogList("Rules", r2.getName() + "[Condition]" + Arrays.toString(split), "N", new ArrayList<>());
                nodeList.add(cNode);
            }
        }

        return addNodesToGraph(parentId, nodeList);
    }

    private boolean addActionsToRule(String parentId, IRRule r1, IRRule r2) {
        List<IRNode> nodeList = new ArrayList<>();

        Set<String> actionInString1 = r1.getActions().stream().map(x -> x.getProject() + "####" + x.getName() + "####" + x.getValue()).collect(Collectors.toSet());
        Set<String> actionInString2 = r2.getActions().stream().map(x -> x.getProject() + "####" + x.getName() + "####" + x.getValue()).collect(Collectors.toSet());

        for (String c1 : actionInString1) {
            if (!actionInString2.contains(c1)) {
                String[] split = c1.split("####");
                IRNode aNode = new IRNode(Arrays.toString(split), new ArrayList<>(), "D");
                addItemToChangelogList("Rules", r1.getName() + "[Action]" + Arrays.toString(split), "D", new ArrayList<>());
                nodeList.add(aNode);
            }
        }

        for (String c2 : actionInString2) {
            if (!actionInString1.contains(c2)) {
                String[] split = c2.split("####");
                IRNode aNode = new IRNode(Arrays.toString(split), new ArrayList<>(), "N");
                addItemToChangelogList("Rules", r2.getName() + "[Action]" + Arrays.toString(split), "N", new ArrayList<>());
                nodeList.add(aNode);
            }
        }

        return addNodesToGraph(parentId, nodeList);
    }

    private void getChange(List<Change> array, String field, String o, String o2) {
        if (!o.equals(o2)) {
            array.add(new Change(field, o, o2));
        }
    }

    private boolean createIntermediateNode(String parentId, String intermediateName, List<IRNode> nodeList) {
        boolean changeParentNode = false;
        if (!nodeList.isEmpty()) {
            // If the intermediate node has any change we add it to the nodes list
            IRNode intermediateNode = new IRNode(intermediateName, "");
            addNode(intermediateNode);
            addLink(parentId, intermediateNode.getId());

            // We add the child nodes and link them to the parent node
            for (IRNode n : nodeList) {
                addNode(n);
                addLink(intermediateNode.getId(), n.getId());
            }

            changeParentNode = true;

        }

        return changeParentNode;
    }

    private void addNode(IRNode n) {
        graph.getNodes().add(n);
    }

    private void addLink(String parentId, String childId) {
        graph.getLinks().add(new Link(parentId, childId));
    }

    private boolean addNodesToGraph(String parentId, List<IRNode> nodeList) {
        boolean changeParentNode = false;
        if (!nodeList.isEmpty()) {
            for (IRNode n : nodeList) {
                addNode(n);
                addLink(parentId, n.getId());
            }
            changeParentNode = true;
        }

        return changeParentNode;
    }

    private void addItemToChangelogList(String element, String elementRef, String action, List<Change> changes) {
        addItemToChangelogList(graph, element, elementRef, action, changes);
    }

    private void addItemToChangelogList(Graph targetGraph, String element, String elementRef, String action, List<Change> changes) {
        ChangelogItem ch = new ChangelogItem();
        ch.setElement(element);
        ch.setElementRef(elementRef);
        ch.setAction(action);
        switch (action) {
            case "N":
                ch.setInfo("The element " + elementRef + " has been added");
                break;
            case "D":
                ch.setInfo("The element " + elementRef + " has been deleted");
                break;
            case "E":
                ch.setInfo("The element " + elementRef + " has been modified");
                break;
            case "":
                break;
        }
        ch.setChanges(changes);
        targetGraph.getChangelogList().add(ch);
    }


    public String createChangelogBetweenVersionsSimple() {
        JSONObject json = new JSONObject();
        GraphList gl = getVersionChanges();
        HashSet<String> itemsAllowed = new HashSet<>();
        itemsAllowed.add("RiskPattern");
        itemsAllowed.add("Component Definitions");
        itemsAllowed.add("Supported Standards");
        itemsAllowed.add("Usecases");
        itemsAllowed.add("Threats");
        itemsAllowed.add("Weaknesses");
        itemsAllowed.add("Controls");
        itemsAllowed.add("Rules");

        HashMap<String, TreeSet<String>> map = new HashMap<>();

        for (Graph g : gl.getGraphs().values()) {
            for (ChangelogItem item : g.getChangelogList()) {
                if (itemsAllowed.contains(item.getElement())) {
                    String element = item.getElement();

                    if (!json.has(element)) {
                        json.put(element, new JSONArray());
                        map.put(element, new TreeSet<>());
                    }

                    JSONArray array = json.getJSONArray(element);

                    if (!map.get(element).contains(item.getElementRef())) {
                        map.get(element).add(item.getElementRef());

                        JSONObject obj = new JSONObject();
                        JSONArray changes = new JSONArray();
                        for (Change i : item.getChanges()) {
                            changes.put(i.getField());
                        }

                        if (!changes.isEmpty()) {
                            obj.put("changes", changes);
                        } else {
                            obj.put("changes", new JSONArray());
                        }

                        obj.put("ref", item.getElementRef());
                        obj.put("action", item.getAction());

                        if ("E".equals(item.getAction()) && changes.isEmpty()) {
                            continue;
                        }
                        if ("E".equals(item.getAction()) && changes.length() == 1 && changes.toList().contains("timestamp")) {
                            continue;
                        }

                        array.put(obj);
                    }


                }
            }
        }

        Set<String> keys = new HashSet<>();
        for (String key : json.keySet()) {
            JSONArray array = json.getJSONArray(key);
            if (array.isEmpty()) {
                keys.add(key);
            }
        }
        for (String key : keys) {
            json.remove(key);
        }

        return json.toString();

    }

    public ChangelogReport generateRelationsChangelog() {
        ChangelogReport report = new ChangelogReport();

        List<IRExtendedRelation> oldRelations = new ArrayList<>();
        for (IRLibrary l : fv.getLibraries().values()) {
            for (IRRelation rel : l.getRelations().values()) {
                oldRelations.add(new IRExtendedRelation(l.getRef(), rel.getRiskPatternUuid(), rel));
            }
        }

        List<IRExtendedRelation> newRelations = new ArrayList<>();
        for (IRLibrary l : sv.getLibraries().values()) {
            for (IRRelation rel : l.getRelations().values()) {
                newRelations.add(new IRExtendedRelation(l.getRef(), rel.getRiskPatternUuid(), rel));
            }
        }


        Set<IRExtendedRelation> deleted = new HashSet<>(oldRelations);
        newRelations.forEach(deleted::remove);

        report.setDeleted(deleted);

        Set<IRExtendedRelation> added = new HashSet<>(newRelations);
        oldRelations.forEach(added::remove);

        report.setAdded(added);

        HashMap<String, List<IRExtendedRelation>> newCountermeasures = new HashMap<>();

        for (IRExtendedRelation c : newRelations) {
            if ("".equals(c.getControlRef())) {
                continue;
            }
            if (!fv.getControls().containsKey(c.getControlRef())) {
                if (!newCountermeasures.containsKey(c.getControlRef())) {
                    List<IRExtendedRelation> tmp = new ArrayList<>();
                    tmp.add(c);
                    newCountermeasures.put(c.getControlRef(), tmp);
                } else {
                    newCountermeasures.get(c.getControlRef()).add(c);
                }
            }
        }

        report.setNewCountermeasures(newCountermeasures);

        return report;
    }

    public Set<String> getListFromRelations(IRLibrary l, String attrib) {
        Set<String> valuesInLibrary = new HashSet<>();
        for (IRRelation r : l.getRelations().values()) {
            switch (attrib) {
                case "controls":
                    valuesInLibrary.add(r.getControlUuid());
                    break;
                case "weaknesses":
                    valuesInLibrary.add(r.getWeaknessUuid());
                    break;
                case "threats":
                    valuesInLibrary.add(r.getThreatUuid());
                    break;
                case "usecases":
                    valuesInLibrary.add(r.getUsecaseUuid());
                    break;
            }


        }
        valuesInLibrary.removeIf(item -> item == null || item.isEmpty());

        return valuesInLibrary;
    }

    private Set<String> getCategoriesOfComponents(IRLibrary lib, ILEVersion version) {
        // Get all category references from component definitions
        Set<String> categoryRefs = lib.getComponentDefinitions().values().stream()
                .map(IRComponentDefinition::getCategoryRef)
                .collect(Collectors.toSet());

        // Convert category references to UUIDs by looking up the categories in the version
        Set<String> categoryUuids = new HashSet<>();
        for (String categoryRef : categoryRefs) {
            // Find the category by reference and get its UUID
            for (IRCategoryComponent category : version.getCategories().values()) {
                if (category.getRef().equals(categoryRef)) {
                    categoryUuids.add(category.getUuid());
                    break;
                }
            }
        }

        return categoryUuids;
    }

    public LibrarySummariesResponse getLibrarySummaries() {
        LibrarySummariesResponse response = new LibrarySummariesResponse();
        
        // Get added libraries
        List<LibrarySummary> added = new ArrayList<>();
        for (String libraryName : sv.getLibraries().keySet()) {
            if (!fv.getLibraries().containsKey(libraryName)) {
                IRLibrary library = sv.getLibrary(libraryName);
                added.add(new LibrarySummary(
                    library.getRef(),
                    library.getName(),
                    "ADDED",
                    null,
                    library.getRevision(),
                    true
                ));
            }
        }
        response.setAddedLibraries(added);
        
        // Get deleted libraries
        List<LibrarySummary> deleted = new ArrayList<>();
        for (String libraryName : fv.getLibraries().keySet()) {
            if (!sv.getLibraries().containsKey(libraryName)) {
                IRLibrary library = fv.getLibrary(libraryName);
                deleted.add(new LibrarySummary(
                    library.getRef(),
                    library.getName(),
                    "DELETED",
                    library.getRevision(),
                    null,
                    true
                ));
            }
        }
        response.setDeletedLibraries(deleted);
        
        // Get modified libraries
        List<LibrarySummary> modified = new ArrayList<>();
        for (String libraryName : fv.getLibraries().keySet()) {
            if (sv.getLibraries().containsKey(libraryName)) {
                IRLibrary oldLibrary = fv.getLibrary(libraryName);
                IRLibrary newLibrary = sv.getLibrary(libraryName);
                
                // Check if there are actual changes
                boolean hasChanges = !oldLibrary.getRevision().equals(newLibrary.getRevision()) ||
                                   !oldLibrary.getName().equals(newLibrary.getName()) ||
                                   !oldLibrary.getDesc().equals(newLibrary.getDesc()) ||
                                   !oldLibrary.getFilename().equals(newLibrary.getFilename()) ||
                                   !oldLibrary.getEnabled().equals(newLibrary.getEnabled());
                
                modified.add(new LibrarySummary(
                    newLibrary.getRef(),
                    newLibrary.getName(),
                    "MODIFIED",
                    oldLibrary.getRevision(),
                    newLibrary.getRevision(),
                    hasChanges
                ));
            }
        }
        response.setModifiedLibraries(modified);
        
        return response;
    }

    public Graph getLibrarySpecificChanges(String libraryRef) {
        // Find the library in both versions
        IRLibrary firstLibrary = null;
        IRLibrary secondLibrary = null;
        
        for (IRLibrary lib : fv.getLibraries().values()) {
            if (lib.getRef().equals(libraryRef)) {
                firstLibrary = lib;
                break;
            }
        }
        
        for (IRLibrary lib : sv.getLibraries().values()) {
            if (lib.getRef().equals(libraryRef)) {
                secondLibrary = lib;
                break;
            }
        }
        
        if (firstLibrary == null && secondLibrary == null) {
            throw new IllegalArgumentException("Library not found: " + libraryRef);
        }
        
        // Create a new graph for this specific library comparison
        Graph graph = new Graph();
        
        if (firstLibrary == null) {
            // This is a new library (added)
            IRNode root = new IRNode(secondLibrary.getRef(), new ArrayList<>(), "N");
            addItemToChangelogList(graph, "Library", secondLibrary.getRef(), "N", new ArrayList<>());
            graph.getNodes().add(root);
            graph.setRevFirst(null);
            graph.setRevSecond(secondLibrary.getRevision());
        } else if (secondLibrary == null) {
            // This is a deleted library
            IRNode root = new IRNode(firstLibrary.getRef(), new ArrayList<>(), "D");
            addItemToChangelogList(graph, "Library", firstLibrary.getRef(), "D", new ArrayList<>());
            graph.getNodes().add(root);
            graph.setRevFirst(firstLibrary.getRevision());
            graph.setRevSecond(null);
        } else {
            // This is a modified library - use the existing logic
            this.first = firstLibrary;
            this.second = secondLibrary;
            graph = getLibraryChanges();
        }
        
        return graph;
    }


}
