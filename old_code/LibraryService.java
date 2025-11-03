package com.iriusrisk.editor.services;

import com.iriusrisk.editor.configuration.ILEConstants;
import com.iriusrisk.editor.exceptions.ILEException;
import com.iriusrisk.editor.facades.IOFacade;
import com.iriusrisk.editor.models.ILEVersion;
import com.iriusrisk.editor.models.IRBaseElement;
import com.iriusrisk.editor.models.elements.IRComponentDefinition;
import com.iriusrisk.editor.models.elements.IRLibrary;
import com.iriusrisk.editor.models.elements.IRRelation;
import com.iriusrisk.editor.models.elements.IRRiskPattern;
import com.iriusrisk.editor.models.elements.IRRiskPatternItem;
import com.iriusrisk.editor.models.elements.IRRule;
import com.iriusrisk.editor.models.elements.IRRuleAction;
import com.iriusrisk.editor.models.elements.IRRuleCondition;
import com.iriusrisk.editor.models.elements.IRThreatItem;
import com.iriusrisk.editor.models.elements.IRUseCaseItem;
import com.iriusrisk.editor.models.graph.Graph;
import com.iriusrisk.editor.models.graph.Link;
import com.iriusrisk.editor.models.graph.RuleNode;
import com.iriusrisk.editor.models.reports.IRLibraryReport;
import com.iriusrisk.editor.models.reports.IRMitigationItem;
import com.iriusrisk.editor.models.reports.IRMitigationReport;
import com.iriusrisk.editor.models.reports.IRMitigationRiskPattern;
import com.iriusrisk.editor.models.request.ComponentRequest;
import com.iriusrisk.editor.models.request.LibraryUpdateRequest;
import com.iriusrisk.editor.models.request.RelationRequest;
import com.iriusrisk.editor.models.request.RiskPatternRequest;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.stereotype.Service;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.function.Function;
import java.util.stream.Collectors;

import lombok.RequiredArgsConstructor;

import static java.util.stream.Collectors.toList;
import static java.util.stream.Collectors.toSet;

@Service
@RequiredArgsConstructor
public class LibraryService {

    private static final Logger logger = LogManager.getLogger(LibraryService.class);

    private final DataService dataService;
    private final IOFacade ioFacade;
    private final List<String[]> exceptions = new ArrayList<>(Arrays.asList(
            new String[]{"GENERIC-SERVICE:AUTHN-SF", "CAPEC-16"},
            new String[]{"GENERIC-SERVICE:DATA-SENS:AUTHZ", "CAPEC-232"}
    ));

    public IRLibraryReport createLibraryReport(String versionRef, String libraryRef) {
        return dataService.createLibraryReport(versionRef, libraryRef);
    }

    public void exportLibrary(String versionRef, String libraryRef, String format) {
        IRLibrary lib = dataService.getLibrary(versionRef, libraryRef);

        if ("xml".equals(format)) {

            try {
                File f = new File(ILEConstants.OUTPUT_FOLDER + "/" + versionRef);
                f.mkdirs();
                ioFacade.exportLibraryXML(lib, dataService.getVersion(versionRef), ILEConstants.OUTPUT_FOLDER + "/" + versionRef);
            } catch (Exception e) {
                throw new ILEException("Couldn't export to XML");
            }

        } else if ("xlsx".equals(format)) {
            try {
                File f = new File(ILEConstants.OUTPUT_FOLDER + "/" + versionRef);
                f.mkdirs();
                ioFacade.exportLibraryXLSX(lib, dataService.getVersion(versionRef), ILEConstants.OUTPUT_FOLDER + "/" + versionRef);
            } catch (Exception e) {
                throw new ILEException("Couldn't export to XLSX");
            }
        }

    }

    public Graph createRulesGraph(String versionRef, String libraryRef) {
        Graph g = new Graph();
        g.setDirected(true);
        g.setMultigraph(false);
        IRLibrary lib = dataService.getLibrary(versionRef, libraryRef);
        List<IRRule> rules = lib.getRules();
        TreeMap<String, IRRiskPattern> riskPatterns = lib.getRiskPatterns();
        Map<String, IRComponentDefinition> componentDefinitions = lib.getComponentDefinitions().values().stream().collect(Collectors.toMap(IRBaseElement::getRef, Function.identity()));

        for (IRRule r : rules) {
            Set<String> conditionIds = new HashSet<>();
            for (IRRuleCondition c : r.getConditions()) {
                RuleNode newCondition = new RuleNode(c.getName(), c.getValue(), "CONDITION", componentDefinitions);
                if (!g.hasNodeValue(newCondition.getId())) {
                    g.getNodes().add(newCondition);
                }

                conditionIds.add(newCondition.getId());
            }

            for (IRRuleAction a : r.getActions()) {
                RuleNode newAction = new RuleNode(a.getName(), a.getValue(), "ACTION", riskPatterns);

                if (!g.hasNodeValue(newAction.getId())) {
                    g.getNodes().add(newAction);
                }

                for (String cond : conditionIds) {
                    g.getLinks().add(new Link(cond, newAction.getId()));
                }

            }


        }


        return g;
    }

    public IRMitigationReport checkMitigation(String versionRef, String libraryRef) {
        ILEVersion version = dataService.getVersion(versionRef);
        IRLibrary lib = version.getLibrary(libraryRef);

        IRMitigationReport report = new IRMitigationReport();

        for (IRRiskPattern rp : lib.getRiskPatterns().values()) {
            IRMitigationRiskPattern s = new IRMitigationRiskPattern(rp.getRef());
            HashMap<String, IRRiskPatternItem> riskPatternTree = dataService.getRelationsInTree(lib);
            IRRiskPatternItem rpItem = riskPatternTree.get(rp.getUuid());
            
            if (rpItem != null) {
                for (IRUseCaseItem uc : rpItem.getUsecases().values()) {

                    for (IRThreatItem t : uc.getThreats().values()) {

                        // If threat is an exception we continue to the next one
                        boolean pass = false;
                        for (String[] except : exceptions) {
                            if (rp.getRef().equals(except[0]) && t.getRef().equals(except[1])) {
                                pass = true;
                                break;
                            }
                        }
                        if (pass) {
                            continue;
                        }

                        // First part: find if the threat has incorrect mitigation values
                        int mitigationCount = 0;

                        Set<IRRelation> threatRels = lib.getRelations().values().stream()
                                .filter(x -> x.getRiskPatternUuid().equals(rp.getUuid()) &&
                                        x.getUsecaseUuid().equals(uc.getRef()) &&
                                        x.getThreatUuid().equals(t.getRef()))
                                .collect(toSet());

                        Set<String> alreadyChecked = new HashSet<>();
                        for (IRRelation rel : threatRels) {
                            if (!"".equals(rel.getControlUuid()) && !alreadyChecked.contains(rel.getControlUuid())) {
                                alreadyChecked.add(rel.getControlUuid());
                                mitigationCount += Integer.parseInt(rel.getMitigation());
                            }

                        }

                        String message = "";
                        boolean error = false;

                        if (mitigationCount != 100) {
                            message = "Error with mitigation: " + mitigationCount;
                            error = true;
                        }

                        if (error) {
                            logger.info("Risk pattern: " + rp.getRef() + " -> " + t.getRef());
                            logger.info(message);
                            logger.info("Total mitigation: " + (mitigationCount));

                            IRMitigationItem item = new IRMitigationItem();
                            item.setUsecaseRef(uc.getRef());
                            item.setThreatRef(t.getRef());
                            item.setMessage(message);
                            item.setTotal("" + mitigationCount);
                            item.setRelations(threatRels);
                            item.setError(true);

                            s.getThreats().add(item);

                        }
                    }

                }
            }

            if (!s.getThreats().isEmpty()) {
                report.getRiskPatterns().add(s);
            }
        }

        return report;
    }

    /**
     * Balance mitigation values to be 100 for every threat in the library
     */
    public void balanceMitigation(String versionRef, String libraryRef) {
        ILEVersion version = dataService.getVersion(versionRef);
        IRLibrary lib = version.getLibrary(libraryRef);

        logger.info("Balancing mitigations...");
        for (IRRiskPattern rp : lib.getRiskPatterns().values()) {
            logger.info("RP:" + rp.getRef());
            HashMap<String, IRRiskPatternItem> riskPatternTree = dataService.getRelationsInTree(lib);
            IRRiskPatternItem rpItem = riskPatternTree.get(rp.getUuid());
            
            if (rpItem != null) {
                for (IRUseCaseItem uc : rpItem.getUsecases().values()) {

                    for (IRThreatItem t : uc.getThreats().values()) {

                        // If threat is an exception we continue to the next one
                        boolean pass = false;
                        for (String[] except : exceptions) {
                            if (rp.getRef().equals(except[0]) && t.getRef().equals(except[1])) {
                                pass = true;
                                break;
                            }
                        }
                        if (pass) {
                            continue;
                        }

                        // First part: find if the threat has incorrect mitigation values
                        logger.info("T: " + t.getRef());
                        List<IRRelation> relationList = new ArrayList<>();
                        List<IRRelation> threatRels = lib.getRelations().values().stream()
                                .filter(x -> x.getRiskPatternUuid().equals(rp.getUuid()) &&
                                        x.getUsecaseUuid().equals(uc.getRef()) &&
                                        x.getThreatUuid().equals(t.getRef())).collect(toList());

                        for (IRRelation rel : threatRels) {
                            if (!"".equals(rel.getControlUuid())) {
                                relationList.add(rel);
                            }
                        }

                        fixMitigationValues(relationList, 100);
                    }

                }
            }
        }

        logger.info("Balanced!");
    }

    private void fixMitigationValues(List<IRRelation> all, int goal) {
        if (!all.isEmpty()) {
            // Check first if the mitigation sum the given value
            int mitigationSum = 0;
            for (IRRelation rel : all) {
                mitigationSum += Integer.parseInt(rel.getMitigation());
            }

            if (mitigationSum != goal) {
                logger.info("Sum is " + mitigationSum + " (Desired: " + goal + "). Fixing threat...");
                int mean = goal / all.size();
                int remainder = goal % all.size();
                for (IRRelation rel : all) {
                    int newMit = mean;

                    if (remainder != 0) {
                        newMit += remainder;
                        remainder = 0;
                    }

                    if (!rel.getMitigation().equals("" + newMit)) {
                        logger.info("Control: Updated mitigation for " + rel.getControlUuid() + ": " + rel.getMitigation() + " -> " + newMit);
                        rel.setMitigation("" + newMit);
                    } else {
                        logger.info("No changes for " + rel.getControlUuid());
                    }
                }
            }
        }

    }




    // Libraries

    public void updateLibrary(String versionRef, String libraryRef, LibraryUpdateRequest newLib) {
        IRLibrary currentLib = dataService.getLibrary(versionRef, libraryRef);
        currentLib.setName(newLib.getName());
        currentLib.setDesc(newLib.getDesc());
        currentLib.setRevision(newLib.getRevision());
        currentLib.setFilename(newLib.getFilename());
        currentLib.setEnabled(newLib.getEnabled());
    }

    // Components

    public Collection<IRComponentDefinition> listComponents(String versionRef, String library) {
        return dataService.getLibrary(versionRef, library).getComponentDefinitions().values();
    }

    public IRComponentDefinition addComponent(String versionRef, String lib, ComponentRequest body) {
        ILEVersion v = dataService.getVersion(versionRef);
        IRLibrary l = v.getLibrary(lib);
        IRComponentDefinition comp = new IRComponentDefinition(body.getRef(), body.getName(), body.getDesc(), body.getCategoryRef(), body.getVisible());
        l.getComponentDefinitions().put(comp.getUuid(), comp);
        return comp;
    }

    public IRComponentDefinition updateComponent(String versionRef, String lib, IRComponentDefinition newComp) {
        ILEVersion v = dataService.getVersion(versionRef);
        IRLibrary l = v.getLibrary(lib);
        l.getComponentDefinitions().put(newComp.getUuid(), newComp);
        return newComp;
    }

    public void deleteComponent(String versionRef, String lib, IRComponentDefinition comp) {
        ILEVersion v = dataService.getVersion(versionRef);
        IRLibrary l = v.getLibrary(lib);
        l.getComponentDefinitions().remove(comp.getUuid());
    }

    // Risk patterns

    public Collection<IRRiskPattern> listRiskPatterns(String versionRef, String library) {
        return dataService.getLibrary(versionRef, library).getRiskPatterns().values();
    }

    public IRRiskPattern addRiskPattern(String versionRef, String libraryRef, RiskPatternRequest request) {
        ILEVersion v = dataService.getVersion(versionRef);
        IRLibrary l = v.getLibrary(libraryRef);
        IRRiskPattern rp = new IRRiskPattern(request.getRef(), request.getName(), request.getDesc());
        l.getRiskPatterns().put(rp.getUuid(), rp);
        return rp;
    }

    public IRRiskPattern updateRiskPattern(String versionRef, String lib, RiskPatternRequest newRp) {
        ILEVersion v = dataService.getVersion(versionRef);
        IRLibrary l = v.getLibrary(lib);
        IRRiskPattern rp = l.getRiskPatterns().get(newRp.getUuid());
        if(newRp.getRef()!=null){
            rp.setRef(newRp.getRef());
        }

        if(newRp.getName()!=null){
            rp.setName(newRp.getName());
        }

        if(newRp.getDesc()!=null){
            rp.setDesc(newRp.getDesc());
        }

        l.getRiskPatterns().put(rp.getUuid(), rp);
        return rp;
    }

    public void deleteRiskPattern(String versionRef, String lib, IRRiskPattern rp) {
        ILEVersion v = dataService.getVersion(versionRef);
        IRLibrary l = v.getLibrary(lib);
        l.getRiskPatterns().remove(rp.getUuid());
    }

    // Relations

    public Collection<IRRelation> listRelations(String versionRef, String library) {
        return dataService.getLibrary(versionRef, library).getRelations().values();
    }

    public IRRelation addRelation(String versionRef, String lib, RelationRequest body) {
        ILEVersion v = dataService.getVersion(versionRef);
        IRLibrary l = v.getLibrary(lib);
        IRRelation rel = new IRRelation(body.getRiskPatternUuid(), body.getUsecaseUuid(), body.getThreatUuid(), body.getWeaknessUuid(), body.getControlUuid(), body.getMitigation());
        l.getRelations().put(rel.getUuid(), rel);
        return rel;
    }

    public IRRelation updateRelation(String versionRef, String lib, IRRelation newRel) {
        ILEVersion v = dataService.getVersion(versionRef);
        IRLibrary l = v.getLibrary(lib);
        l.getRelations().put(newRel.getUuid(), newRel);
        return newRel;
    }

    public void deleteRelation(String versionRef, String lib, IRRelation rel) {
        ILEVersion v = dataService.getVersion(versionRef);
        IRLibrary l = v.getLibrary(lib);
        l.getRelations().remove(rel.getUuid());
    }

}
