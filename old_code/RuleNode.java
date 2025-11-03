package com.iriusrisk.editor.models.graph;

import com.iriusrisk.editor.models.elements.IRComponentDefinition;
import com.iriusrisk.editor.models.elements.IRRiskPattern;

import java.util.Map;
import java.util.TreeMap;
import java.util.UUID;

import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
public class RuleNode extends Node {
    private String message;
    private String color;

    public RuleNode(String name, String value, String field, Map<String, IRComponentDefinition> components) {
        super();
        if (value != null && !value.isEmpty()) {
            setValueForConditionNode(name, value, field, components);
        }
        // Hardcoded
        if(name.equals("CONDITION_DATAFLOW_CROSS_TRUST_BOUNDARY")){
            setValueForConditionNode(name, value, field, components);
        }
    }

    public RuleNode(String name, String value, String project, TreeMap<String, IRRiskPattern> riskPatterns) {
        super();
        if (value != null && !value.isEmpty()) {
            setValueForActionNode(name, value, project, riskPatterns);
        }
    }

    /**
     * Library objects here is the list of component definitions
     */
    private void setValueForConditionNode(String name, String value, String field, Map<String, IRComponentDefinition> components) {
        switch (name) {
            case "CONDITION_COMPONENT_DEFINITION":
                this.setId(value);
                if (components.containsKey(this.getId())) {
                    message = "Is specific component definition: " + components.get(this.getId()).getName();
                } else {
                    message = "Is specific component definition: " + this.getId();
                }
                color = "#000080";
                break;
            case "CONDITION_QUESTION_GROUP_EXISTS":
            case "CONDITION_COMPONENT_QUESTION_GROUP_EXISTS":
                String[] valueList;
                valueList = value.split("_::_");
                this.setId(valueList[0]);
                message = "If question group '" + this.getId() + "' exists";
                color = "#00FFFF";
                break;
            case "CONDITION_QUESTION":
            case "CONDITION_COMPONENT_QUESTION":
                this.setId(value);
                message = "If answer is " + this.getId();
                color = "#00FF00";
                break;
            case "CONDITION_QUESTION_NOT_ANSWERED":
            case "CONDITION_COMPONENT_QUESTION_NOT_ANSWERED":
                this.setId(value);
                message = "If answer is not " + this.getId();
                color = "#008080";
                break;
            case "CONDITION_RISK_PATTERN_EXISTS":
                this.setId(value);
                message = "Risk pattern " + this.getId().split("_::_")[0] + " -> " + this.getId().split("_::_")[1] + " exists";
                color = "#800000";
                break;
            case "CONDITION_CONCLUSION_EXISTS":
            case "CONDITION_CONCLUSION_COMPONENT_EXISTS":
                this.setId(value);
                message = "Conclusion " + this.getId() + " exists";
                color = "#0000FF";
                break;
            case "CONDITION_CONCLUSION_NOT_EXISTS":
            case "CONDITION_CONCLUSION_COMPONENT_NOT_EXISTS":

                this.setId(value);
                message = "Conclusion " + this.getId() + " not exists";
                color = "#FF00FF";
                break;
            case "CONDITION_APPLIED_CONTROL":
                this.setId(value);
                message = "Countermeasure " + this.getId() + " is required";
                color = "#800080";
                break;
            case "CONDITION_DATAFLOW_CONTAINS_TAG":
                this.setId(value);
                message = "Dataflow contains tag '" + this.getId()+"'";
                color = "#800080";
                break;
            case "CONDITION_CLASSIFICATION":
                this.setId(value);
                message = "Dataflow contains asset of type '" + this.getId() + "'";
                color = "#800080";
                break;
            case "CONDITION_ORIGIN_TRUSTZONE":
                this.setId(value);
                message = "Trustzone at origin is " + this.getId();
                color = "#800080";
                break;
            case "CONDITION_DESTINATION_TRUSTZONE":
                this.setId(value);
                message = "Trustzone at destination is " + this.getId();
                color = "#800080";
                break;
            case "CONDITION_DATAFLOW_CROSS_TRUST_BOUNDARY":
                this.setId(UUID.randomUUID().toString());
                message = "Trustzone crosses boundary";
                color = "#800080";
                break;
            case "CONDITION_DATAFLOW_RISK_PATTERN_IN_ORIGIN":
                this.setId(value);
                message = "Risk pattern "+this.getId()+" is in origin";
                color = "#800080";
                break;
            case "CONDITION_DATAFLOW_RISK_PATTERN_IN_DESTINATION":
                this.setId(value);
                message = "Risk pattern "+this.getId()+" is in destination";
                color = "#800080";
                break;
            case "CONDITION_DATAFLOW_CONTAINS_ASSET":
                this.setId(value);
                message = "Asset "+this.getId()+" is in dataflow";
                color = "#800080";
                break;
            default:
                this.setId(UUID.randomUUID().toString());
                message = "Unknown: " + name;
                color = "#C0C0C0";


        }
    }

    /**
     * Library objects here is the list of risk patterns
     */
    private void setValueForActionNode(String name, String value, String project, TreeMap<String, IRRiskPattern> riskPatterns) {
        String[] valueList;
        switch (name) {
            case "INSERT_QUESTION_GROUP":
            case "INSERT_COMPONENT_QUESTION_GROUP":
                valueList = value.split("_::_");
                this.setId(valueList[0]);
                this.message = "Question: " + valueList[2];
                this.color = "#f6ec48";
                break;
            case "INSERT_QUESTION":
            case "INSERT_COMPONENT_QUESTION":
                valueList = value.split("_::_");
                this.setId(valueList[0]);
                message = "Answer: " + valueList[1];
                color = "#008000";
                break;
            case "IMPORT_RISK_PATTERN":
                valueList = value.split("_::_");
                this.setId(valueList[1]);
                if (riskPatterns.get(this.getId()) != null) {
                    message = "Import Risk Pattern: " + riskPatterns.get(this.getId()).getName();
                    color = "#FF4500";
                } else {
                    message = "Import Risk Pattern (Not found!): " + this.getId();
                    color = "#000000";
                }
                break;
            case "EXTEND_RISK_PATTERN":
                valueList = value.split("_::_");
                this.setId(value);
                message = "Extend Risk Pattern " + valueList[0] + " >> " + valueList[1];
                color = "#FFA07A";
                break;
            case "INSERT_CONCLUSION":
            case "INSERT_COMPONENT_CONCLUSION":
                valueList = value.split("_::_");
                this.setId(valueList[1]);
                message = "Conclusion: " + valueList[2];
                color = "#F0E68C";
                break;
            case "APPLY_CONTROL":
                this.setId(project + "_::_" + value);
                message = "Apply Control: " + project + " -> " + this.getId();
                color = "#663399";
                break;
            case "MARK_CONTROL_AS":
                valueList = value.split("_::_");
                this.setId(valueList[0]);
                message = "Apply Control: " + project + " -> " + this.getId();
                color = "#663399";
                break;
            case "APPLY_SECURITY_STANDARD":
                valueList = value.split("_::_");
                this.setId(valueList[1]);
                message = "Apply security standard: " + this.getId();
                color = "#FFA500";
                break;
            case "ANSWER_QUESTION":
            case "ANSWER_COMPONENT_QUESTION":
                valueList = value.split("_::_");
                this.setId(valueList[0]);
                message = "Answered question: " + this.getId();
                color = "#6A5ACD";
                break;
            case "IMPORT_SPECIFIC_UC":
                valueList = value.split("_::_");
                this.setId(valueList[1]+"_::_"+valueList[2]);
                message = "Imported use case: " + valueList[2]+" from risk pattern "+valueList[1];
                color = "#5A5ACD";
                break;
            case "IMPORT_RISK_PATTERN_ORIGIN":
                valueList = value.split("_::_");
                this.setId(valueList[1]);
                if (riskPatterns.get(this.getId()) != null) {
                    message = "Import Risk Pattern in origin: " + riskPatterns.get(this.getId()).getName();
                    color = "#FF4500";
                } else {
                    message = "Import Risk Pattern in origin (Not found!): " + this.getId();
                    color = "#000000";
                }
                break;
            case "IMPORT_RISK_PATTERN_DESTINATION":
                valueList = value.split("_::_");
                this.setId(valueList[1]);
                if (riskPatterns.get(this.getId()) != null) {
                    message = "Import Risk Pattern in destination: " + riskPatterns.get(this.getId()).getName();
                    color = "#FF4500";
                } else {
                    message = "Import Risk Pattern in destination (Not found!): " + this.getId();
                    color = "#000000";
                }
                break;
            case "IMPLEMENT_CONTROL_ORIGIN":
                this.setId(project + "_::_" + value);
                message = "Apply Control in origin: " + project + " -> " + this.getId();
                color = "#663399";
                break;
            case "IMPLEMENT_CONTROL_DESTINATION":
                this.setId(project + "_::_" + value);
                message = "Apply Control in destination: " + project + " -> " + this.getId();
                color = "#663399";
                break;
            case "INSERT_DATAFLOW_NOTIFICATION":
                valueList = value.split("_::_");
                this.setId(valueList[1]);
                message = "Notify (from dataflow): " + valueList[2];
                color = "#663399";
                break;
            case "INSERT_COMPONENT_NOTIFICATION":
                valueList = value.split("_::_");
                this.setId(valueList[1]);
                message = "Notify (from component): " + valueList[2];
                color = "#663399";
                break;
            case "INSERT_CONCLUSION_ORIGIN_COMPONENT":
                valueList = value.split("_::_");
                this.setId(valueList[1]);
                message = "Insert conclusion in origin: " + valueList[2];
                color = "#663399";
                break;
            case "INSERT_CONCLUSION_DESTINATION_COMPONENT":
                valueList = value.split("_::_");
                this.setId(valueList[1]);
                message = "Insert conclusion in destination: " + valueList[2];
                color = "#663399";
                break;
            case "INSERT_COMPONENT_ALERT":
                valueList = value.split("_::_");
                this.setId(valueList[1]);
                message = "Notify (from component): " + valueList[2];
                color = "#663399";
                break;
            default:
                this.setId(UUID.randomUUID().toString());
                message = "Unknown: " + name;
                color = "#00FF7F";

        }

    }


    public String toString() {
        return "[ " + this.getId() + " / " + this.message + " ]";
    }
}
