import InlineEditor from '@ckeditor/ckeditor5-build-inline';
import CKEditor from '@ckeditor/ckeditor5-react';
import Accordion from "@material-ui/core/Accordion";
import AccordionDetails from "@material-ui/core/AccordionDetails";
import AccordionSummary from "@material-ui/core/AccordionSummary";
import Button from "@material-ui/core/Button";
import Container from '@material-ui/core/Container';
import CssBaseline from '@material-ui/core/CssBaseline';
import FormControl from "@material-ui/core/FormControl";
import Grid from "@material-ui/core/Grid";
import InputLabel from "@material-ui/core/InputLabel";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import Select from "@material-ui/core/Select";
import { withStyles } from '@material-ui/core/styles';
import TextField from "@material-ui/core/TextField";
import Typography from "@material-ui/core/Typography";
import ClearIcon from '@material-ui/icons/Clear';
import axios from "axios";
import MaterialTable from "material-table";
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { excelDelimiter, sortArrayByKey } from "../../utils/commonFunctions";
import { easyToast, failedToast, successToast } from "../../utils/toastFunctions";
import QuickAddReferences from "./QuickAddReferences";

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

const ManageControls = (props) => {
    const { classes, version: initialVersion } = props;
    const [version] = useState(initialVersion);
    const [data, setData] = useState([]);
    const dataRef = useRef([]);

    const addControl = useCallback((control) => {
        axios.post('/api/version/' + version + '/control', control)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Add the returned object from the API to the state
                    setData(prevData => [...prevData, res.data]);
                    dataRef.current = [...dataRef.current, res.data];
                    successToast("Control added");
                } else {
                    failedToast("Control couldn't be added");
                }
            })
            .catch(err => failedToast(err));
    }, [version]);

    const updateControl = useCallback((updatedControl) => {
        axios.put('/api/version/' + version + '/control', updatedControl)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Update the state with the returned object from the API
                    setData(prevData => {
                        const newData = prevData.map(item => 
                            item.uuid === updatedControl.uuid ? res.data : item
                        );
                        return newData;
                    });
                    dataRef.current = dataRef.current.map(item => 
                        item.uuid === updatedControl.uuid ? res.data : item
                    );
                    easyToast(res, "Control updated", "Control couldn't be updated");
                }
            })
            .catch(err => failedToast(err));
    }, [version]);

    const updateControlSilent = useCallback((updatedControl) => {
        // Update the ref without triggering a re-render
        dataRef.current = dataRef.current.map(item => 
            item.uuid === updatedControl.uuid ? updatedControl : item
        );
    }, []);

    const deleteControls = useCallback((rowData) => {
        axios.delete('/api/version/' + version + '/control', {data: rowData})
            .then(res => {
                if (res.status === 200) {
                    successToast("Control/s deleted");
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
            .catch(err => failedToast("Control/s couldn't be deleted: " + err));
    }, [version]);

    useEffect(() => {
        axios.get('/api/version/' + version + '/control',)
            .then(res => {
                setData(res.data);
                dataRef.current = res.data;
            })
            .catch(err => failedToast(err));
    }, [version]);

    return (
        <div className={classes.root}>
            <CssBaseline/>
            <Container maxWidth="lg" className={classes.container}>
                <div>
                    <Typography variant="h4">
                        Manage controls
                    </Typography>
                    <MaterialTable
                        title="Controls"
                        columns={[
                            {title: 'Ref', editable: 'onAdd', field: 'ref'},
                            {title: 'Name', editable: 'always', field: 'name'},
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
                            },
                            {
                                title: 'Standards', searchable: false, hidden: true, field: 'standards',
                                // customFilterAndSearch: (value, rowData) => {
                                //     if (typeof rowData.standards !== "undefined") {
                                //         let s = rowData.standards.filter(
                                //             x => x.standard_ref.toUpperCase().startsWith(value.toUpperCase()) ||
                                //                  x.supported_standard_ref.toUpperCase()
                                //                      .startsWith(value.toUpperCase())).length;
                                //         return s > 0;
                                //     } else {
                                //         return false;
                                //     }
                                // },
                                render: rowData => {
                                    return JSON.stringify(rowData.standards);
                                }
                            }
                        ]}
                        data={data}
                        key="controls-table"
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
                                tooltip: 'Remove All Selected Controls',
                                icon: 'delete',
                                onClick: (evt, rowData) => deleteControls(rowData)
                            }
                        ]}
                        detailPanel={rowData => {
                            return (
                                <ControlDetailPanel 
                                    version={version} 
                                    rowData={rowData} 
                                    onUpdate={updateControlSilent}
                                />
                            )
                        }}
                        editable={{
                            onRowAdd: newData =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        if (newData.name === undefined) {
                                            newData.name = "";
                                        }
                                        // Prepare control data matching ControlRequest structure
                                        const controlData = {
                                            ref: newData.ref || "",
                                            name: newData.name || "",
                                            desc: "",
                                            state: "Recommended",
                                            cost: "0",
                                            steps: "",
                                            base_standard: [],
                                            base_standard_section: [],
                                            scope: [],
                                            mitre: []
                                        };
                                        addControl(controlData);
                                        resolve();
                                    }, 100)
                                }),
                            onRowUpdate: (newData, oldData) =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        const updatedControl = {
                                            uuid: oldData.uuid,
                                            ref: newData.ref,
                                            name: newData.name,
                                            desc: oldData.desc || "",
                                            state: oldData.state || "Recommended",
                                            cost: oldData.cost || "0",
                                            references: oldData.references || [],
                                            standards: oldData.standards || [],
                                            base_standard: oldData.base_standard || [],
                                            base_standard_section: oldData.base_standard_section || [],
                                            scope: oldData.scope || [],
                                            mitre: oldData.mitre || [],
                                            test: oldData.test || {
                                                steps: "",
                                                result: "",
                                                timestamp: "",
                                                references: [],
                                            }
                                        };
                                        updateControl(updatedControl);
                                        resolve();
                                    }, 100)
                                }),
                            onRowDelete: oldData =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        deleteControls([oldData]);
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

const ControlDetailPanel = (props) => {
    const { version, rowData: initialRowData, onUpdate } = props;
    const [data, setData] = useState(initialRowData);
    const [librarySuggestions, setLibrarySuggestions] = useState([]);
    const [referenceSuggestions, setReferenceSuggestions] = useState([]);
    const [relationSuggestions, setRelationSuggestions] = useState([]);
    const [standardSuggestions, setStandardSuggestions] = useState([]);
    const [accordion, setAccordion] = useState(false);
    const [newBaseStandardItem, setNewBaseStandardItem] = useState("");
    const [newBaseStandardSectionItem, setNewBaseStandardSectionItem] = useState("");
    const [newScopeItem, setNewScopeItem] = useState("");
    const [newMitreItem, setNewMitreItem] = useState("");

    const loadSuggestions = useCallback(() => {
        // Load suggestions only if we have a ref
        if (data.ref) {
            let postdata = {
                type: "control",
                ref: data.ref
            };
            axios.post('/api/version/' + version + '/suggestions', postdata)
                .then(res => {
                    setLibrarySuggestions(res.data.librarySuggestions || []);
                    setRelationSuggestions(res.data.relationSuggestions || []);
                })
                .catch(err => {
                    console.error('Error loading suggestions:', err);
                    // Don't show error toast for suggestions as it's not critical
                });
        }
        
        // Load references (version-wide resources)
        axios.get('/api/version/' + version + '/reference')
            .then(res => {
                setReferenceSuggestions(sortArrayByKey(res.data || [], "name"));
            })
            .catch(err => {
                console.error('Error loading references:', err);
                failedToast("Could not load references");
            });
        
        // Load standards (version-wide resources)
        axios.get('/api/version/' + version + '/standard')
            .then(res => {
                setStandardSuggestions(sortArrayByKey(res.data || [], "standard_ref"));
            })
            .catch(err => {
                console.error('Error loading standards:', err);
                failedToast("Could not load standards");
            });
    }, [version, data.ref]);

    useEffect(() => {
        loadSuggestions();
    }, [loadSuggestions]);

    const updateControlBody = (event) => {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const postdata = {
            uuid: formData.get('uuid') || "",
            ref: formData.get('ref') || "",
            name: formData.get('name') || "",
            desc: data.desc || "",
            state: formData.get('state') || "Recommended",
            cost: formData.get('cost') || "0",
            steps: data.test?.steps || "",
            base_standard: data.base_standard || [],
            base_standard_section: data.base_standard_section || [],
            scope: data.scope || [],
            mitre: data.mitre || []
        };
        axios.put('/api/version/' + version + '/control', postdata)
            .then(res => {
                if (res.status === 200 && res.data) {
                    setData(res.data);
                    if (onUpdate) {
                        onUpdate(res.data);
                    }
                    easyToast(res, "Control updated", "Control couldn't be updated");
                }
            })
            .catch(err => {
                console.error('Error updating control:', err);
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

    const addReference = (event) => {
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
        const referenceExists = Object.values(data.references || {}).includes(referenceObj.uuid);
        if (referenceExists) {
            failedToast("Reference " + referenceValue + " already exists in this control");
            return;
        }
        
        // Call the API to add reference
        const referenceItemRequest = {
            item_uuid: data.uuid,
            item_type: "CONTROL",
            reference_uuid: referenceObj.uuid
        };
        
        axios.put('/api/version/' + version + '/control/reference', referenceItemRequest)
            .then(res => {
                if (res.status === 200 && res.data) {
                    setData(res.data);
                    if (onUpdate) {
                        onUpdate(res.data);
                    }
                    successToast("Reference added successfully");
                }
            })
            .catch(err => {
                console.error('Error adding reference:', err);
                failedToast(err);
            });
    };

    const deleteReference = (referenceUuid) => {
        // Call the API to delete reference
        const referenceItemRequest = {
            item_uuid: data.uuid,
            item_type: "CONTROL",
            reference_uuid: referenceUuid
        };
        
        axios.delete('/api/version/' + version + '/control/reference', { data: referenceItemRequest })
            .then(res => {
                if (res.status === 200 && res.data) {
                    setData(res.data);
                    if (onUpdate) {
                        onUpdate(res.data);
                    }
                    successToast("Reference removed successfully");
                }
            })
            .catch(err => {
                console.error('Error removing reference:', err);
                failedToast(err);
            });
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
            failedToast("Test reference " + referenceValue + " already exists in this control");
            return;
        }
        
        // Call the API to add reference
        const referenceItemRequest = {
            item_uuid: data.uuid,
            item_type: "CONTROL_TEST",
            reference_uuid: referenceObj.uuid
        };
        
        axios.put('/api/version/' + version + '/control/reference', referenceItemRequest)
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
            item_type: "CONTROL_TEST",
            reference_uuid: referenceUuid
        };
        
        axios.delete('/api/version/' + version + '/control/reference', { data: referenceItemRequest })
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

    const addStandard = (event) => {
        const standardValue = event.target.value;
        if (!standardValue || standardValue.trim() === "") {
            return;
        }
        
        // Find the standard object by standard_ref
        const standardObj = standardSuggestions.find(std => std.standard_ref === standardValue);
        if (!standardObj) {
            failedToast("Standard not found");
            return;
        }
        
        // Check if standard already exists
        const standardExists = Object.values(data.standards || {}).includes(standardObj.uuid);
        if (standardExists) {
            failedToast("Standard " + standardValue + " already exists in this control");
            return;
        }
        
        // Call the API to add standard
        const standardItemRequest = {
            item_uuid: data.uuid,
            item_type: "CONTROL",
            standard_uuid: standardObj.uuid
        };
        
        axios.put('/api/version/' + version + '/control/standard', standardItemRequest)
            .then(res => {
                if (res.status === 200 && res.data) {
                    setData(res.data);
                    if (onUpdate) {
                        onUpdate(res.data);
                    }
                    successToast("Standard added successfully");
                }
            })
            .catch(err => {
                console.error('Error adding standard:', err);
                failedToast(err);
            });
    };

    const deleteStandard = (standardUuid) => {
        // Call the API to delete standard
        const standardItemRequest = {
            item_uuid: data.uuid,
            item_type: "CONTROL",
            standard_uuid: standardUuid
        };
        
        axios.delete('/api/version/' + version + '/control/standard', { data: standardItemRequest })
            .then(res => {
                if (res.status === 200 && res.data) {
                    setData(res.data);
                    if (onUpdate) {
                        onUpdate(res.data);
                    }
                    successToast("Standard removed successfully");
                }
            })
            .catch(err => {
                console.error('Error removing standard:', err);
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

    return (
        <div>
            <form style={classes.form} onSubmit={updateControlBody}>
                {librarySuggestions.length !== 0 &&
                 <div>
                     {librarySuggestions.map((value, index) => {
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
                                                {value.usecase_uuid} / {value.threat_uuid} / {value.weakness_uuid} / {value.control_uuid}
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
                    label="Control ref"
                    defaultValue={data.ref}
                    autoFocus
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="name"
                    name="name"
                    label="Control name"
                    defaultValue={data.name}
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="uuid"
                    name="uuid"
                    label="Control uuid"
                    defaultValue={data.uuid}
                />
                <Typography variant="body1">
                    Description
                </Typography>
                <CKEditor
                    editor={InlineEditor}
                    id="desc"
                    data={data.desc}
                    onBlur={(event, editor) => {
                        handleDescChangeEditor(editor.getData());
                    }}
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="state"
                    name="state"
                    label="Control state"
                    defaultValue={data.state}
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="cost"
                    name="cost"
                    label="Control cost"
                    defaultValue={data.cost}
                />
                <Typography variant="body1">
                    Base Standard
                </Typography>
                <Grid>
                    {data.base_standard && data.base_standard.length > 0 &&
                     <div>
                         { data.base_standard.map((base_standardItem, index) => {
                             return (
                                 <Button 
                                     variant="outlined" 
                                     startIcon={<ClearIcon />} 
                                     className={classes.redHover}
                                     style={{ margin: '4px' }} 
                                     key={index} 
                                     onClick={() => {
                                         const newBaseStandard = data.base_standard.filter((_, i) => i !== index);
                                         setData({...data, base_standard: newBaseStandard});
                                     }}
                                 >
                                     {base_standardItem}
                                 </Button>
                             );
                         })}
                     </div>
                    }
                    <Grid container spacing={2} alignItems="center">
                        <Grid item xs={9}>
                            <TextField
                                variant="outlined"
                                fullWidth
                                value={newBaseStandardItem}
                                onChange={(e) => setNewBaseStandardItem(e.target.value)}
                                placeholder="Add base standard item"
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                        e.preventDefault();
                                        if (newBaseStandardItem.trim()) {
                                            const newBaseStandard = [...(data.base_standard || []), newBaseStandardItem.trim()];
                                            setData({...data, base_standard: newBaseStandard});
                                            setNewBaseStandardItem("");
                                        }
                                    }
                                }}
                            />
                        </Grid>
                        <Grid item xs={3}>
                            <Button
                                variant="contained"
                                color="primary"
                                onClick={() => {
                                    if (newBaseStandardItem.trim()) {
                                        const newBaseStandard = [...(data.base_standard || []), newBaseStandardItem.trim()];
                                        setData({...data, base_standard: newBaseStandard});
                                        setNewBaseStandardItem("");
                                    }
                                }}
                            >
                                Add
                            </Button>
                        </Grid>
                    </Grid>
                </Grid>
                <Typography variant="body1">
                    Base Standard Section
                </Typography>
                <Grid>
                    {data.base_standard_section && data.base_standard_section.length > 0 &&
                     <div>
                         { data.base_standard_section.map((base_standard_sectionItem, index) => {
                             return (
                                 <Button 
                                     variant="outlined" 
                                     startIcon={<ClearIcon />} 
                                     className={classes.redHover}
                                     style={{ margin: '4px' }} 
                                     key={index} 
                                     onClick={() => {
                                         const newBaseStandardSection = data.base_standard_section.filter((_, i) => i !== index);
                                         setData({...data, base_standard_section: newBaseStandardSection});
                                     }}
                                 >
                                     {base_standard_sectionItem}
                                 </Button>
                             );
                         })}
                     </div>
                    }
                    <Grid container spacing={2} alignItems="center">
                        <Grid item xs={9}>
                            <TextField
                                variant="outlined"
                                fullWidth
                                value={newBaseStandardSectionItem}
                                onChange={(e) => setNewBaseStandardSectionItem(e.target.value)}
                                placeholder="Add base standard section item"
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                        e.preventDefault();
                                        if (newBaseStandardSectionItem.trim()) {
                                            const newBaseStandardSection = [...(data.base_standard_section || []), newBaseStandardSectionItem.trim()];
                                            setData({...data, base_standard_section: newBaseStandardSection});
                                            setNewBaseStandardSectionItem("");
                                        }
                                    }
                                }}
                            />
                        </Grid>
                        <Grid item xs={3}>
                            <Button
                                variant="contained"
                                color="primary"
                                onClick={() => {
                                    if (newBaseStandardSectionItem.trim()) {
                                        const newBaseStandardSection = [...(data.base_standard_section || []), newBaseStandardSectionItem.trim()];
                                        setData({...data, base_standard_section: newBaseStandardSection});
                                        setNewBaseStandardSectionItem("");
                                    }
                                }}
                            >
                                Add
                            </Button>
                        </Grid>
                    </Grid>
                </Grid>
                <Typography variant="body1">
                    Scope
                </Typography>
                <Grid>
                    {data.scope && data.scope.length > 0 &&
                     <div>
                         { data.scope.map((scopeItem, index) => {
                             return (
                                 <Button 
                                     variant="outlined" 
                                     startIcon={<ClearIcon />} 
                                     className={classes.redHover}
                                     style={{ margin: '4px' }} 
                                     key={index} 
                                     onClick={() => {
                                         const newScope = data.scope.filter((_, i) => i !== index);
                                         setData({...data, scope: newScope});
                                     }}
                                 >
                                     {scopeItem}
                                 </Button>
                             );
                         })}
                     </div>
                    }
                    <Grid container spacing={2} alignItems="center">
                        <Grid item xs={9}>
                            <TextField
                                variant="outlined"
                                fullWidth
                                value={newScopeItem}
                                onChange={(e) => setNewScopeItem(e.target.value)}
                                placeholder="Add scope item"
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                        e.preventDefault();
                                        if (newScopeItem.trim()) {
                                            const newScope = [...(data.scope || []), newScopeItem.trim()];
                                            setData({...data, scope: newScope});
                                            setNewScopeItem("");
                                        }
                                    }
                                }}
                            />
                        </Grid>
                        <Grid item xs={3}>
                            <Button
                                variant="contained"
                                color="primary"
                                onClick={() => {
                                    if (newScopeItem.trim()) {
                                        const newScope = [...(data.scope || []), newScopeItem.trim()];
                                        setData({...data, scope: newScope});
                                        setNewScopeItem("");
                                    }
                                }}
                            >
                                Add
                            </Button>
                        </Grid>
                    </Grid>
                </Grid>
                <Typography variant="body1">
                    MITRE
                </Typography>
                <Grid>
                    {data.mitre && data.mitre.length > 0 &&
                     <div>
                         { data.mitre.map((mitreItem, index) => {
                             return (
                                 <Button 
                                     variant="outlined" 
                                     startIcon={<ClearIcon />} 
                                     className={classes.redHover}
                                     style={{ margin: '4px' }} 
                                     key={index} 
                                     onClick={() => {
                                         const newMitre = data.mitre.filter((_, i) => i !== index);
                                         setData({...data, mitre: newMitre});
                                     }}
                                 >
                                     {mitreItem}
                                 </Button>
                             );
                         })}
                     </div>
                    }
                    <Grid container spacing={2} alignItems="center">
                        <Grid item xs={9}>
                            <TextField
                                variant="outlined"
                                fullWidth
                                value={newMitreItem}
                                onChange={(e) => setNewMitreItem(e.target.value)}
                                placeholder="Add MITRE item"
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                        e.preventDefault();
                                        if (newMitreItem.trim()) {
                                            const newMitre = [...(data.mitre || []), newMitreItem.trim()];
                                            setData({...data, mitre: newMitre});
                                            setNewMitreItem("");
                                        }
                                    }
                                }}
                            />
                        </Grid>
                        <Grid item xs={3}>
                            <Button
                                variant="contained"
                                color="primary"
                                onClick={() => {
                                    if (newMitreItem.trim()) {
                                        const newMitre = [...(data.mitre || []), newMitreItem.trim()];
                                        setData({...data, mitre: newMitre});
                                        setNewMitreItem("");
                                    }
                                }}
                            >
                                Add
                            </Button>
                        </Grid>
                    </Grid>
                </Grid>
                <Typography variant="body1">
                    References
                </Typography>
                <Grid>
                    {data.references && Object.keys(data.references).length > 0 &&
                     <div>
                         {Object.entries(data.references).map(([key, referenceUuid], index) => {
                             // Find the reference name by UUID
                             const referenceObj = referenceSuggestions.find(ref => ref.uuid === referenceUuid);
                             const referenceName = referenceObj ? referenceObj.name : referenceUuid;
                             
                             return (
                                 <Button 
                                     variant="outlined" 
                                     startIcon={<ClearIcon/>} 
                                     className={classes.redHover}
                                     style={{ margin: '4px' }} 
                                     key={key} 
                                     onClick={() => deleteReference(referenceUuid)}
                                 >
                                     {referenceName}
                                 </Button>
                             );
                         })}
                     </div>
                    }
                    <FormControl variant="filled" className={classes.formControl}>
                        <InputLabel htmlFor="outlined-age-native-simple">Add reference</InputLabel>
                        <Select
                            native
                            value=""
                            onChange={(event) => addReference(event)}
                        >
                            <option key={2345678} disabled value=""></option>
                            {referenceSuggestions.map((value, index) => {
                                return <option key={index} value={value.name}>{value.name} | {value.url}</option>
                            })}
                        </Select>
                    </FormControl>
                    <QuickAddReferences version={version} update={loadSuggestions}/>
                </Grid>
                <Typography variant="body1">
                    Standards
                </Typography>
                <Grid>
                    {data.standards && Object.keys(data.standards).length > 0 &&
                     <div>
                         {Object.entries(data.standards).map(([key, standardUuid], index) => {
                             // Find the standard by UUID
                             const standardObj = standardSuggestions.find(std => std.uuid === standardUuid);
                             const standardName = standardObj ? `${standardObj.supported_standard_ref} (${standardObj.standard_ref})` : standardUuid;
                             
                             return (
                                 <Button 
                                     variant="outlined" 
                                     startIcon={<ClearIcon/>} 
                                     className={classes.redHover}
                                     style={{ margin: '4px' }} 
                                     key={key} 
                                     onClick={() => deleteStandard(standardUuid)}
                                 >
                                     {standardName}
                                 </Button>
                             );
                         })}
                     </div>
                    }
                    <FormControl variant="filled" className={classes.formControl}>
                        <InputLabel htmlFor="outlined-age-native-simple">Add standard</InputLabel>
                        <Select
                            native
                            value=""
                            onChange={(event) => addStandard(event)}
                        >
                            <option key={2345678} disabled value=""></option>
                            {standardSuggestions.map((value, index) => {
                                return <option key={index} value={value.standard_ref}>{value.supported_standard_ref} | {value.standard_ref}</option>
                            })}
                        </Select>
                    </FormControl>
                </Grid>
                <Typography variant="body1">
                    Test steps
                </Typography>
                <CKEditor
                    editor={InlineEditor}
                    data={data.test?.steps}
                    onBlur={(event, editor) => {
                        handleTestStepsChangeEditor(editor.getData());
                    }}
                />
                <Typography variant="body1">
                    Test References
                </Typography>
                <Grid>
                    {data.test?.references && Object.keys(data.test.references).length > 0 &&
                     <div>
                         {Object.entries(data.test.references).map(([key, referenceUuid], index) => {
                             // Find the reference name by UUID
                             const referenceObj = referenceSuggestions.find(ref => ref.uuid === referenceUuid);
                             const referenceName = referenceObj ? referenceObj.name : referenceUuid;
                             
                             return (
                                 <Button 
                                     variant="outlined" 
                                     startIcon={<ClearIcon/>} 
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
                            <option key={2345678} disabled value=""></option>
                            {referenceSuggestions.map((value, index) => {
                                return <option key={index} value={value.name}>{value.name} | {value.url}</option>
                            })}
                        </Select>
                    </FormControl>
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

export default withStyles(useStyles)(ManageControls);