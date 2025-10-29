import React, { useState, useEffect, useCallback, useRef } from 'react';
import {withStyles} from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import {easyToast, failedToast, successToast} from "../../utils/toastFunctions";
import MaterialTable from "material-table";
import CKEditor from '@ckeditor/ckeditor5-react';
import InlineEditor from '@ckeditor/ckeditor5-build-inline';
import Grid from "@material-ui/core/Grid";
import Button from "@material-ui/core/Button";
import FormControl from "@material-ui/core/FormControl";
import InputLabel from "@material-ui/core/InputLabel";
import Select from "@material-ui/core/Select";
import ClearIcon from '@material-ui/icons/Clear';
import TextField from "@material-ui/core/TextField";
import {excelDelimiter, sortArrayByKey} from "../../utils/commonFunctions";
import QuickAddReferences from "./QuickAddReferences";
import Accordion from "@material-ui/core/Accordion";
import AccordionSummary from "@material-ui/core/AccordionSummary";
import AccordionDetails from "@material-ui/core/AccordionDetails";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";

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

const ManageWeaknesses = (props) => {
    const { classes, version: initialVersion } = props;
    const [version] = useState(initialVersion);
    const [data, setData] = useState([]);
    const dataRef = useRef([]);

    const addWeakness = useCallback((weakness) => {
        axios.post('/api/version/'+version+'/weakness', weakness)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Add the returned object from the API to the state
                    setData(prevData => [...prevData, res.data]);
                    dataRef.current = [...dataRef.current, res.data];
                    successToast("Weakness added");
                } else {
                    failedToast("Weakness couldn't be added");
                }
            })
            .catch(err => failedToast(err));
    }, [version]);

    const updateWeakness = useCallback((updatedWeakness) => {
        axios.put('/api/version/'+version+'/weakness', updatedWeakness)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Update the state with the returned object from the API
                    setData(prevData => {
                        const newData = prevData.map(item => 
                            item.uuid === updatedWeakness.uuid ? res.data : item
                        );
                        return newData;
                    });
                    dataRef.current = dataRef.current.map(item => 
                        item.uuid === updatedWeakness.uuid ? res.data : item
                    );
                    easyToast(res, "Weakness updated", "Weakness couldn't be updated");
                }
            })
            .catch(err => failedToast(err));
    }, [version]);

    const updateWeaknessSilent = useCallback((updatedWeakness) => {
        // Update the ref without triggering a re-render
        dataRef.current = dataRef.current.map(item => 
            item.uuid === updatedWeakness.uuid ? updatedWeakness : item
        );
    }, []);

    const deleteWeaknesses = useCallback((rowData) => {
        axios.delete('/api/version/'+version+'/weakness', {data: rowData})
            .then(res => {
                if (res.status === 200) {
                    successToast("Weakness/es deleted");
                    // Remove the deleted items from state using their UUIDs
                    setData(prevData => {
                        const deletedUuids = rowData.map(rd => rd.uuid);
                        const newData = prevData.filter(item => !deletedUuids.includes(item.uuid));
                        return newData;
                    });
                    const deletedUuids = rowData.map(rd => rd.uuid);
                    dataRef.current = dataRef.current.filter(item => !deletedUuids.includes(item.uuid));
                }
            })
            .catch(err => failedToast("Weakness/es couldn't be deleted: " + err));
    }, [version]);

    useEffect(() => {
        axios.get('/api/version/' + version + '/weakness',)
            .then(res => {
                setData(res.data);
                dataRef.current = res.data;
            })
            .catch(err => failedToast(err));
    }, [version]);

    return(
        <div className={classes.root}>
            <CssBaseline />
            <Container maxWidth="lg" className={classes.container}>
                <div>
                    <Typography variant="h4">
                        Manage weaknesses
                    </Typography>
                    <MaterialTable
                        title="Weaknesses"
                        columns={[
                            { title: 'Ref', editable: 'onAdd', field: 'ref' },
                            { title: 'Name', editable: 'always', field: 'name' },
                            {
                                title: 'Description', searchable: true, hidden: true, field: 'desc',
                                customFilterAndSearch: (value, rowData) => {
                                    if (typeof rowData.desc !== "undefined") {
                                        return rowData.desc.toUpperCase().includes(value.toUpperCase());
                                    } else {
                                        return false;
                                    }
                                },
                                render: rowData => {
                                    return JSON.stringify(rowData.desc);
                                }
                            },
                            {
                                title: 'Test Steps', searchable: true, hidden: true, field: 'test.steps',
                                customFilterAndSearch: (value, rowData) => {
                                    if (typeof rowData.test.steps !== "undefined") {
                                        return rowData.test.steps.toUpperCase().includes(value.toUpperCase());
                                    } else {
                                        return false;
                                    }
                                },
                                render: rowData => {
                                    return JSON.stringify(rowData.test.steps);
                                }
                            }
                            ]}
                        data={data}
                        key="weaknesses-table"
                        options={{
                            selection: true,
                            sorting: true,
                            search: true,
                            exportAllData: true,
                            exportDelimiter: excelDelimiter,
                            exportButton: true
                        }}
                        actions={[
                            {
                                tooltip: 'Remove All Selected Weaknesses',
                                icon: 'delete',
                                onClick: (evt, rowData) => deleteWeaknesses(rowData)
                            }
                        ]}
                        detailPanel={rowData => {
                            return (
                                <WeaknessDetailPanel 
                                    version={version} 
                                    rowData={rowData} 
                                    onUpdate={updateWeaknessSilent}
                                />
                            )
                        }}
                        editable={{
                            onRowAdd: newData =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        if(newData.name === undefined){
                                            newData.name = "";
                                        }
                                        newData.desc = "";
                                        newData.impact = "100";
                                        newData.test = {
                                            steps: "",
                                            result: "",
                                            timestamp: "",
                                            references: [],
                                        };
                                        addWeakness(newData);
                                        resolve();
                                    }, 100)
                                }),
                            onRowUpdate: (newData, oldData) =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        const updatedWeakness = {
                                            uuid: oldData.uuid,
                                            ref: newData.ref,
                                            name: newData.name,
                                            desc: oldData.desc || "",
                                            impact: oldData.impact || "100",
                                            test: oldData.test || {
                                                steps: "",
                                                result: "",
                                                timestamp: "",
                                                references: [],
                                            }
                                        };
                                        updateWeakness(updatedWeakness);
                                        resolve();
                                    }, 100)
                                }),
                            onRowDelete: oldData =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        deleteWeaknesses([oldData]);
                                        resolve()
                                    }, 100)
                                }),
                        }}

                    />

                </div>
            </Container>
        </div>
    );
}

const WeaknessDetailPanel = (props) => {
    const { version, rowData: initialRowData, onUpdate } = props;
    const [data, setData] = useState(initialRowData);
    const [librarySuggestions, setLibrarySuggestions] = useState([]);
    const [relationSuggestions, setRelationSuggestions] = useState([]);
    const [referenceSuggestions, setReferenceSuggestions] = useState([]);
    const [accordion, setAccordion] = useState(false);

    const loadSuggestions = useCallback(() => {
        let postdata = {
            type: "weakness",
            ref: data.ref
        };
        axios.post('/api/version/' + version + '/suggestions', postdata)
            .then(res => {
                setLibrarySuggestions(res.data.librarySuggestions);
                setRelationSuggestions(res.data.relationSuggestions);
            })
            .catch(err => failedToast(err));
        axios.get('/api/version/'+version+'/reference', )
            .then(res => {
                setReferenceSuggestions(sortArrayByKey(res.data, "name"));
            })
            .catch(err => failedToast(err));
    }, [version, data.ref]);

    useEffect(() => {
        loadSuggestions();
    }, [loadSuggestions]);

    const updateWeaknessBody = (event) => {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const postdata = {
            uuid: formData.get('uuid') || "",
            ref: formData.get('ref') || "",
            name: formData.get('name') || "",
            desc: data.desc || "",
            impact: formData.get('impact') || "100",
            steps: data.test?.steps || ""
        };
        axios.put('/api/version/'+version+'/weakness', postdata)
            .then(res => {
                if (res.status === 200 && res.data) {
                    setData(res.data);
                    if (onUpdate) {
                        onUpdate(res.data);
                    }
                    easyToast(res, "Weakness updated", "Weakness couldn't be updated");
                }
            })
            .catch(err => {
                console.error('Error updating weakness:', err);
                failedToast(err);
            });
    };

    const handleRelationsAccordion = () => {
        setAccordion(!accordion);
    };

    const handleDescChangeEditor = (editorData) => {
        let newData = {...data};
        newData.desc = editorData;
        setData(newData);
    };

    const handleTestStepsChangeEditor = (editorData) => {
        let newData = {...data};
        newData.test = {...newData.test, steps: editorData};
        setData(newData);
    };

    const addTestReference = (event) => {
        const referenceValue = event.target.value;
        if (!referenceValue || referenceValue.trim() === "") {
            return;
        }
        
        // Find the reference object by name
        const referenceObj = referenceSuggestions.find(ref => ref.name === referenceValue);
        if (!referenceObj) {
            failedToast("Reference not found");
            return;
        }
        
        // Check if reference already exists
        const referenceExists = Object.values(data.test?.references || {}).includes(referenceObj.uuid);
        if (referenceExists) {
            failedToast("Test reference " + referenceValue + " already exists in this weakness");
            return;
        }
        
        // Call the API to add reference
        const referenceItemRequest = {
            item_uuid: data.uuid,
            item_type: "WEAKNESS_TEST",
            reference_uuid: referenceObj.uuid
        };
        
        axios.put('/api/version/' + version + '/weakness/reference', referenceItemRequest)
            .then(res => {
                if (res.status === 200 && res.data) {
                    setData(res.data);
                    if (onUpdate) {
                        onUpdate(res.data);
                    }
                    successToast("Test reference added successfully");
                }
            })
            .catch(err => {
                console.error('Error adding test reference:', err);
                failedToast(err);
            });
    };

    const deleteTestReference = (referenceUuid) => {
        // Call the API to delete reference
        const referenceItemRequest = {
            item_uuid: data.uuid,
            item_type: "WEAKNESS_TEST",
            reference_uuid: referenceUuid
        };
        
        axios.delete('/api/version/' + version + '/weakness/reference', { data: referenceItemRequest })
            .then(res => {
                if (res.status === 200 && res.data) {
                    setData(res.data);
                    if (onUpdate) {
                        onUpdate(res.data);
                    }
                    successToast("Test reference removed successfully");
                }
            })
            .catch(err => {
                console.error('Error removing test reference:', err);
                failedToast(err);
            });
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

    return(
        <div>
            <form style={classes.form} onSubmit={updateWeaknessBody}>
                { librarySuggestions.length !== 0 &&
                  <div>
                      { librarySuggestions.map((value, index) => {
                          return <Button key={index}>{value}</Button>
                      })}
                  </div>
                }
                <Accordion expanded={accordion}>
                    <AccordionSummary
                        aria-controls="panel1a-content"
                        id="panel1a-header"
                        onClick={handleRelationsAccordion}
                    >
                        <Typography variant="h6">Relations</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <List>
                            {relationSuggestions.map((value, index) => {
                                return <ListItem key={index}>
                                    <Grid container spacing={3}>
                                        <Grid item xs={12}>
                                            <Typography>
                                                {value.usecase_ref} / {value.threat_ref} / {value.weakness_ref} / {value.control_ref}
                                            </Typography>
                                        </Grid>
                                    </Grid>
                                </ListItem>
                            })}
                        </List>
                    </AccordionDetails>
                </Accordion>
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="ref"
                    name="ref"
                    label="Weakness ref"
                    defaultValue={data.ref}
                    autoFocus
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="name"
                    name="name"
                    label="Weakness name"
                    defaultValue={data.name}
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="uuid"
                    name="uuid"
                    label="Weakness uuid"
                    defaultValue={data.uuid}
                />
                <Typography variant="body1">
                    Description
                </Typography>
                <CKEditor
                    editor={ InlineEditor }
                    id="desc"
                    data={data.desc}
                    onBlur={ ( event, editor ) => {
                        handleDescChangeEditor(editor.getData());
                    } }
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="impact"
                    name="impact"
                    label="Impact"
                    defaultValue={data.impact}
                />
                <Typography variant="body1">
                    Test steps
                </Typography>
                <CKEditor
                    editor={ InlineEditor }
                    data={data.test?.steps}
                    onBlur={ ( event, editor ) => {
                        handleTestStepsChangeEditor(editor.getData());
                    } }
                />
                <Typography variant="body1">
                    Test References
                </Typography>
                <Grid>
                    {data.test?.references && Object.keys(data.test.references).length > 0 &&
                     <div>
                         { Object.entries(data.test.references).map(([key, referenceUuid], index) => {
                             // Find the reference name by UUID
                             const referenceObj = referenceSuggestions.find(ref => ref.uuid === referenceUuid);
                             const referenceName = referenceObj ? referenceObj.name : referenceUuid;
                             
                             return (
                                 <Button 
                                     variant="outlined" 
                                     startIcon={<ClearIcon />} 
                                     className={classes.redHover}
                                     style={{ margin: '4px' }} 
                                     key={key} 
                                     onClick={() => deleteTestReference(referenceUuid)}
                                 >
                                     {referenceName}
                                 </Button>
                             );
                         })}
                     </div>
                    }
                    <FormControl variant="filled" className={classes.formControl}>
                        <InputLabel htmlFor="outlined-age-native-simple">Add test reference</InputLabel>
                        <Select
                            native
                            value=""
                            onChange={(event) => addTestReference(event)}
                        >
                            <option key={2345678} disabled value=""> </option>
                            {referenceSuggestions.map((value, index) => {
                                return <option key={index} value={value.name}>{value.name} | {value.url}</option>
                            })}
                        </Select>
                    </FormControl>
                    <QuickAddReferences version={version} update={loadSuggestions}/>
                </Grid>
                <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    color="primary"
                >
                    Update
                </Button>
            </form>
        </div>
    );
}

export default withStyles(useStyles)(ManageWeaknesses);