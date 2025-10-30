import React, { useState, useEffect, useCallback } from 'react';
import { withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import { easyToast, failedToast } from "../../utils/toastFunctions";
import CKEditor from '@ckeditor/ckeditor5-react';
import InlineEditor from '@ckeditor/ckeditor5-build-inline';
import Grid from "@material-ui/core/Grid";
import Button from "@material-ui/core/Button";
import FormControl from "@material-ui/core/FormControl";
import InputLabel from "@material-ui/core/InputLabel";
import Select from "@material-ui/core/Select";
import ClearIcon from '@material-ui/icons/Clear';
import AddIcon from '@material-ui/icons/Add';
import TextField from "@material-ui/core/TextField";
import { sortArrayByKey } from "../../utils/commonFunctions";
import { 
    ELEMENT_TYPES, 
    getDefaultFormData, 
    extractFormData 
} from "../../utils/ElementCreationService";
import { useElementCreation } from "../../utils/useElementCreation";

const useStyles = (theme) => ({
    root: {
        display: 'flex',
    },
    container: {
        paddingTop: theme.spacing(4),
        paddingBottom: theme.spacing(4),
    },
    formControl: {
        margin: theme.spacing(1),
        minWidth: 120,
    },
    redHover: {
        "&:hover": {
            backgroundColor: "#ff574d",
        },
        "&:active": {
            backgroundColor: "#d94843",
        },
    }
});

const CreateElements = (props) => {
    const [version] = useState(props.version);
    const [elementType, setElementType] = useState("Use case");
    // Use the custom hook for element creation
    const { isCreating, createElement } = useElementCreation(version);
    
    // Form data state
    const [formData, setFormData] = useState(getDefaultFormData());

    // Suggestions and references state
    const [referenceSuggestions, setReferenceSuggestions] = useState([]);
    const [standard_refs, setStandardRefs] = useState(new Map());
    const [standardValues, setStandardValues] = useState([]);
    const [selectedStandard, setSelectedStandard] = useState("");

    const loadSuggestions = useCallback(() => {
        axios.get('/api/version/' + version + '/reference',)
            .then(res => {
                setReferenceSuggestions(sortArrayByKey(res.data, "name"));
            })
            .catch(err => failedToast(err));

        axios.get('/api/version/' + version + '/standard',)
            .then(res => {
                let mymap = new Map();
                res.data.forEach(o => {
                    if (mymap.has(o.supported_standard_ref)) {
                        mymap.set(o.supported_standard_ref, [...mymap.get(o.supported_standard_ref), o])
                    } else {
                        mymap.set(o.supported_standard_ref, [])
                    }
                });

                mymap.forEach((value, key) => {
                    sortArrayByKey(value, "standard_ref");
                });
                mymap = new Map([...mymap].sort());

                setStandardRefs(mymap);
            })
            .catch(err => failedToast(err));
    }, [version]);

    useEffect(() => {
        loadSuggestions();
    }, [loadSuggestions]);

    const handleSubmit = async (event) => {
        event.preventDefault();
        
        try {
            // Extract form data
            const data = extractFormData(event, formData);

            // Create element using the hook
            await createElement(elementType, data);
            easyToast({ status: 200 }, elementType + " added successfully", elementType + " couldn't be added");
            
            // Reset form data for next element
            setFormData(getDefaultFormData());
            
        } catch (error) {
            failedToast(elementType + " couldn't be added: " + error.message);
        }
    };

    // Form field update handlers
    const updateFormData = (field, value) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const updateNestedFormData = (parent, field, value) => {
        setFormData(prev => ({
            ...prev,
            [parent]: {
                ...prev[parent],
                [field]: value
            }
        }));
    };

    const handleDescChangeEditor = (data) => {
        updateFormData('desc', data);
    };

    const handleTestStepsChangeEditor = (data) => {
        updateNestedFormData('test', 'steps', data);
    };

    // Reference management
    const addReference = (event) => {
        const value = event.target.value;
        if (!value) return;
        
        setFormData(prevData => {
            const index = prevData.references.indexOf(value);
            if (index === -1) {
                return {
                    ...prevData,
                    references: [...prevData.references, value]
                };
            } else {
                failedToast("Reference " + value + " already exists in this element");
                return prevData;
            }
        });
    };

    const deleteReference = (value) => {
        setFormData(prevData => {
            const index = prevData.references.indexOf(value);
            if (index > -1) {
                const newReferences = [...prevData.references];
                newReferences.splice(index, 1);
                return {
                    ...prevData,
                    references: newReferences
                };
            }
            return prevData;
        });
    };

    const addTestReference = (event) => {
        const value = event.target.value;
        if (!value) return;
        
        setFormData(prevData => {
            const index = prevData.test.references.indexOf(value);
            if (index === -1) {
                return {
                    ...prevData,
                    test: {
                        ...prevData.test,
                        references: [...prevData.test.references, value]
                    }
                };
            } else {
                failedToast("Test reference " + value + " already exists in this element");
                return prevData;
            }
        });
    };

    const deleteTestReference = (value) => {
        setFormData(prevData => {
            const index = prevData.test.references.indexOf(value);
            if (index > -1) {
                const newTestReferences = [...prevData.test.references];
                newTestReferences.splice(index, 1);
                return {
                    ...prevData,
                    test: {
                        ...prevData.test,
                        references: newTestReferences
                    }
                };
            }
            return prevData;
        });
    };

    // Standard management
    const addStandard = (value) => {
        setFormData(prevData => {
            const index = prevData.standards.indexOf(value);
            if (index === -1) {
                return {
                    ...prevData,
                    standards: [...prevData.standards, value]
                };
            } else {
                failedToast(
                    "Standard " + value.supported_standard_ref + "(" + value.standard_ref + ") already exists in this element");
                return prevData;
            }
        });
    };

    const deleteStandard = (value) => {
        setFormData(prevData => {
            const index = prevData.standards.indexOf(value);
            if (index > -1) {
                const newStandards = [...prevData.standards];
                newStandards.splice(index, 1);
                return {
                    ...prevData,
                    standards: newStandards
                };
            }
            return prevData;
        });
    };

    const getStandardRefs = (event) => {
        const value = event.target.value;
        setSelectedStandard(value);
        setStandardValues(standard_refs.get(value) || []);
    };

    const setElementTypeHandler = (event) => {
        setElementType(event.target.value);
    };

    const classes = {
        form: {
            paddingLeft: "24px",
            paddingRight: "24px",
            backgroundColor: "#e1f0ff"
        },
        redHover: {
            "&:hover": {
                backgroundColor: "#ff574d",
            },
            "&:active": {
                backgroundColor: "#d94843",
            },
        }
    };

    const config = ELEMENT_TYPES[elementType];

    return (
        <div className={classes.root}>
            <CssBaseline/>
            <Container maxWidth="lg" className={classes.container}>
                <div style={{marginTop: "50px"}}>
                    <Typography variant="h4">
                        Create new element
                    </Typography>

                    <form style={classes.form} onSubmit={handleSubmit}>
                        <FormControl variant="filled" className={classes.formControl}>
                            <InputLabel htmlFor="outlined-age-native-simple">Element type</InputLabel>
                            <Select
                                native
                                value={elementType}
                                onChange={setElementTypeHandler}
                            >
                                {Object.keys(ELEMENT_TYPES).map((type, index) => (
                                    <option key={index} value={type}>{type}</option>
                                ))}
                            </Select>
                        </FormControl>
                        
                        <TextField
                            variant="outlined"
                            margin="normal"
                            fullWidth
                            id="ref"
                            label="Element ref"
                            defaultValue={formData.ref}
                        />
                        <TextField
                            variant="outlined"
                            margin="normal"
                            fullWidth
                            id="name"
                            label="Element name"
                            defaultValue={formData.name}
                        />
                        <Typography variant="body1">
                            Description
                        </Typography>
                        <CKEditor
                            editor={InlineEditor}
                            id="desc"
                            data={formData.desc}
                            onBlur={(event, editor) => {
                                handleDescChangeEditor(editor.getData());
                            }}
                        />

                        {/* Control-specific fields */}
                        {config.fields.includes('state') && config.fields.includes('cost') &&
                         <div>
                             <TextField
                                 variant="outlined"
                                 margin="normal"
                                 fullWidth
                                 id="state"
                                 label="Control state"
                                 defaultValue={formData.state}
                             />
                             <TextField
                                 variant="outlined"
                                 margin="normal"
                                 fullWidth
                                 id="cost"
                                 label="Control cost"
                                 defaultValue={formData.cost}
                             />
                             
                             {/* Standards section */}
                             {config.fields.includes('standards') &&
                              <div>
                                  <Typography variant="body1">
                                      Standards
                                  </Typography>
                                  <Grid>
                                      {formData.standards.length > 0 &&
                                       <div>
                                           {formData.standards.map((value, index) => {
                                               return <Button variant="outlined" startIcon={<ClearIcon/>}
                                                              style={classes.redHover}
                                                              key={index} onClick={() => deleteStandard(
                                                   value)}>{value.supported_standard_ref} ({value.standard_ref})</Button>
                                           })}
                                       </div>
                                      }
                                      <FormControl variant="filled" className={classes.formControl}>
                                          <InputLabel htmlFor="outlined-age-native-simple">Add standard</InputLabel>
                                          <Select
                                              native
                                              value={selectedStandard}
                                              onChange={getStandardRefs}
                                          >
                                              <option key={2345678} disabled value=""></option>
                                              {[...standard_refs.keys()].map((value, index) => {
                                                  return <option key={index}
                                                                 value={value}>{value}</option>
                                              })}
                                          </Select>
                                      </FormControl>

                                      {selectedStandard !== "" &&
                                       <div>
                                           {standardValues.map((value, index) => {
                                               return <Button variant="outlined" startIcon={<AddIcon/>}
                                                              style={classes.redHover}
                                                              key={index} onClick={() => addStandard(
                                                   value)}>{value.standard_ref}</Button>
                                           })}
                                       </div>
                                      }
                                  </Grid>
                              </div>
                             }
                         </div>
                        }

                        {/* Threat-specific fields */}
                        {config.fields.includes('riskRating') &&
                         <div>
                             <TextField
                                 variant="outlined"
                                 margin="normal"
                                 fullWidth
                                 id="confidentiality"
                                 label="Confidentiality"
                                 defaultValue={formData.riskRating.confidentiality}
                             />
                             <TextField
                                 variant="outlined"
                                 margin="normal"
                                 fullWidth
                                 id="integrity"
                                 label="Integrity"
                                 defaultValue={formData.riskRating.integrity}
                             />
                             <TextField
                                 variant="outlined"
                                 margin="normal"
                                 fullWidth
                                 id="availability"
                                 label="Availability"
                                 defaultValue={formData.riskRating.availability}
                             />
                             <TextField
                                 variant="outlined"
                                 margin="normal"
                                 fullWidth
                                 id="ease_of_exploitation"
                                 label="Ease of Exploitation"
                                 defaultValue={formData.riskRating.ease_of_exploitation}
                             />
                         </div>
                        }

                        {/* Weakness-specific fields */}
                        {config.fields.includes('impact') &&
                         <div>
                             <TextField
                                 variant="outlined"
                                 margin="normal"
                                 fullWidth
                                 id="impact"
                                 label="Impact"
                                 defaultValue={formData.impact}
                             />
                         </div>
                        }

                        {/* References section */}
                        {config.fields.includes('references') &&
                         <div>
                             <Typography variant="body1">
                                 References
                             </Typography>
                             <Grid>
                                 {formData.references.length > 0 &&
                                  <div>
                                      {formData.references.map((value, index) => {
                                          return <Button variant="outlined" startIcon={<ClearIcon/>}
                                                         style={classes.redHover}
                                                         key={index} onClick={() => deleteReference(
                                              value)}>{value}</Button>
                                      })}
                                  </div>
                                 }
                                 <FormControl variant="filled" className={classes.formControl}>
                                     <InputLabel htmlFor="outlined-age-native-simple">Add reference</InputLabel>
                                     <Select
                                         native
                                         value=""
                                         onChange={addReference}
                                     >
                                         <option key={2345678} disabled value=""></option>
                                         {referenceSuggestions.map((value, index) => {
                                             return <option key={index}
                                                            value={value.name}>{value.name} | {value.url}</option>
                                         })}
                                     </Select>
                                 </FormControl>
                             </Grid>
                         </div>
                        }

                        {/* Test section */}
                        {config.fields.includes('test') &&
                         <div>
                             <Typography variant="body1">
                                 Test steps
                             </Typography>
                             <CKEditor
                                 editor={InlineEditor}
                                 data={formData.test.steps}
                                 onBlur={(event, editor) => {
                                     handleTestStepsChangeEditor(editor.getData());
                                 }}
                             />
                             <Typography variant="body1">
                                 Test References
                             </Typography>
                             <Grid>
                                 {formData.test.references.length > 0 &&
                                  <div>
                                      {formData.test.references.map((value, index) => {
                                          return <Button variant="outlined" startIcon={<ClearIcon/>}
                                                         style={classes.redHover}
                                                         key={index}
                                                         onClick={() => deleteTestReference(
                                                             value)}>{value}</Button>
                                      })}
                                  </div>
                                 }
                                 <FormControl variant="filled" className={classes.formControl}>
                                     <InputLabel htmlFor="outlined-age-native-simple">Add test
                                         reference</InputLabel>
                                     <Select
                                         native
                                         value=""
                                         onChange={addTestReference}
                                     >
                                         <option key={2345678} disabled value=""></option>
                                         {referenceSuggestions.map((value, index) => {
                                             return <option key={index}
                                                            value={value.name}>{value.name} | {value.url}</option>
                                         })}
                                     </Select>
                                 </FormControl>
                             </Grid>
                         </div>
                        }

                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            color="primary"
                            disabled={isCreating}
                        >
                            {isCreating ? "Creating..." : "Create"}
                        </Button>
                    </form>
                </div>
            </Container>
        </div>
    );
};

export default withStyles(useStyles)(CreateElements);