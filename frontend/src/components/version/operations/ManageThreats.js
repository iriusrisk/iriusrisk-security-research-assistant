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

const ManageThreats = (props) => {
    const { classes, version: initialVersion } = props;
    const [version] = useState(initialVersion);
    const [data, setData] = useState([]);
    const dataRef = useRef([]);

    const addThreat = useCallback((threat) => {
        axios.post('/api/version/'+version+'/threat', threat)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Add the returned object from the API to the state
                    setData(prevData => [...prevData, res.data]);
                    dataRef.current = [...dataRef.current, res.data];
                    successToast("Threat added");
                } else {
                    failedToast("Threat couldn't be added");
                }
            })
            .catch(err => failedToast(err));
    }, [version]);

    const updateThreat = useCallback((updatedThreat) => {
        axios.put('/api/version/'+version+'/threat', updatedThreat)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Update the state with the returned object from the API
                    setData(prevData => {
                        const newData = prevData.map(item => 
                            item.uuid === updatedThreat.uuid ? res.data : item
                        );
                        return newData;
                    });
                    dataRef.current = dataRef.current.map(item => 
                        item.uuid === updatedThreat.uuid ? res.data : item
                    );
                    easyToast(res, "Threat updated", "Threat couldn't be updated");
                }
            })
            .catch(err => failedToast(err));
    }, [version]);

    const updateThreatSilent = useCallback((updatedThreat) => {
        // Update the ref without triggering a re-render
        dataRef.current = dataRef.current.map(item => 
            item.uuid === updatedThreat.uuid ? updatedThreat : item
        );
    }, []);

    const deleteThreats = useCallback((rowData) => {
        axios.delete('/api/version/'+version+'/threat', {data: rowData})
            .then(res => {
                if (res.status === 200) {
                    successToast("Threat/s deleted");
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
            .catch(err => failedToast("Threat/s couldn't be deleted: " + err));
    }, [version]);

    useEffect(() => {
        axios.get('/api/version/' + version + '/threat',)
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
                        Manage threats
                    </Typography>
                    <MaterialTable
                        title="Threats"
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
                            }
                            ]}
                        data={data}
                        key="threats-table"
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
                                tooltip: 'Remove All Selected Threats',
                                icon: 'delete',
                                onClick: (evt, rowData) => deleteThreats(rowData)
                            }
                        ]}
                        detailPanel={rowData => {
                            return (
                                <ThreatDetailPanel 
                                    version={version} 
                                    rowData={rowData} 
                                    onUpdate={updateThreatSilent}
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
                                        newData.riskRating = {
                                            confidentiality: "100",
                                            integrity: "100",
                                            availability: "100",
                                            ease_of_exploitation: "100"
                                        };
                                        newData.references = [];
                                        newData.mitre = [];
                                        newData.stride = [];

                                        addThreat(newData);
                                        resolve();
                                    }, 100)
                                }),
                            onRowUpdate: (newData, oldData) =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        const updatedThreat = {
                                            uuid: oldData.uuid,
                                            ref: newData.ref,
                                            name: newData.name,
                                            desc: oldData.desc || "",
                                            riskRating: oldData.riskRating || {
                                                confidentiality: "100",
                                                integrity: "100",
                                                availability: "100",
                                                ease_of_exploitation: "100"
                                            },
                                            mitre: oldData.mitre || [],
                                            stride: oldData.stride || [],
                                            referencesToAdd: [],
                                            referencesToDelete: []
                                        };
                                        updateThreat(updatedThreat);
                                        resolve();
                                    }, 100)
                                }),
                            onRowDelete: oldData =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        deleteThreats([oldData]);
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

const ThreatDetailPanel = (props) => {
    const { version, rowData: initialRowData, onUpdate } = props;
    const [data, setData] = useState(initialRowData);
    const [librarySuggestions, setLibrarySuggestions] = useState([]);
    const [relationSuggestions, setRelationSuggestions] = useState([]);
    const [referenceSuggestions, setReferenceSuggestions] = useState([]);
    const [accordion, setAccordion] = useState(false);
    const [newMitreItem, setNewMitreItem] = useState("");
    const [newStrideItem, setNewStrideItem] = useState("");

    const loadSuggestions = useCallback(() => {
        let postdata = {
            type: "threat",
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



    const updateThreatBody = (event) => {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const postdata = {
            uuid: formData.get('uuid') || "",
            ref: formData.get('ref') || "",
            name: formData.get('name') || "",
            desc: data.desc || "",
            riskRating: {
                confidentiality: formData.get('confidentiality') || "",
                integrity: formData.get('integrity') || "",
                availability: formData.get('availability') || "",
                ease_of_exploitation: formData.get('ease_of_exploitation') || "",
            },
            mitre: data.mitre || [],
            stride: data.stride || []
        };
        axios.put('/api/version/'+version+'/threat', postdata)
            .then(res => {
                if (res.status === 200 && res.data) {
                    setData(res.data);
                    if (onUpdate) {
                        onUpdate(res.data);
                    }
                    easyToast(res, "Threat updated", "Threat couldn't be updated");
                }
            })
            .catch(err => {
                console.error('Error updating threat:', err);
                failedToast(err);
            });
    };

    const handleRelationsAccordion = () => {
        setAccordion(!accordion);
    };

    const handleDescChangeEditor = (data) => {
        let newData = {...data};
        newData.desc = data;
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
            failedToast("Reference " + referenceValue + " already exists in this threat");
            return;
        }
        
        // Call the API to add reference
        const referenceItemRequest = {
            itemUuid: data.uuid,
            itemType: "THREAT",
            referenceUuid: referenceObj.uuid
        };
        
        axios.put('/api/version/' + version + '/threat/reference', referenceItemRequest)
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
            itemUuid: data.uuid,
            itemType: "THREAT",
            referenceUuid: referenceUuid
        };
        
        axios.delete('/api/version/' + version + '/threat/reference', { data: referenceItemRequest })
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
            <form style={classes.form} onSubmit={updateThreatBody}>
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
                                                {value.usecaseRef} / {value.threatRef} / {value.weaknessRef} / {value.controlRef}
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
                    label="Threat ref"
                    defaultValue={data.ref}
                    autoFocus
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="name"
                    name="name"
                    label="Threat name"
                    defaultValue={data.name}
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="uuid"
                    name="uuid"
                    label="Threat uuid"
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
                    id="confidentiality"
                    name="confidentiality"
                    label="Confidentiality"
                    defaultValue={data.riskRating?.confidentiality || "100"}
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="integrity"
                    name="integrity"
                    label="Integrity"
                    defaultValue={data.riskRating?.integrity || "100"}
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="availability"
                    name="availability"
                    label="Availability"
                    defaultValue={data.riskRating?.availability || "100"}
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="ease_of_exploitation"
                    name="ease_of_exploitation"
                    label="Ease of Exploitation"
                    defaultValue={data.riskRating?.ease_of_exploitation || "100"}
                />
                <Typography variant="body1">
                    Mitre
                </Typography>
                <Grid>
                    {data.mitre && data.mitre.length > 0 &&
                     <div>
                         { data.mitre.map((mitreItem, index) => {
                             return (
                                 <Button 
                                     variant="outlined" 
                                     startIcon={<ClearIcon />} 
                                     
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
                                placeholder="Add mitre item"
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
                    STRIDE
                </Typography>
                <Grid>
                    {data.stride && data.stride.length > 0 &&
                     <div>
                         { data.stride.map((strideItem, index) => {
                             return (
                                 <Button 
                                     variant="outlined" 
                                     startIcon={<ClearIcon />} 
                                     className={classes.redHover}
                                     style={{ margin: '4px' }} 
                                     key={index} 
                                     onClick={() => {
                                         const newStride = data.stride.filter((_, i) => i !== index);
                                         setData({...data, stride: newStride});
                                     }}
                                 >
                                     {strideItem}
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
                                value={newStrideItem}
                                onChange={(e) => setNewStrideItem(e.target.value)}
                                placeholder="Add STRIDE item"
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                        e.preventDefault();
                                        if (newStrideItem.trim()) {
                                            const newStride = [...(data.stride || []), newStrideItem.trim()];
                                            setData({...data, stride: newStride});
                                            setNewStrideItem("");
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
                                    if (newStrideItem.trim()) {
                                        const newStride = [...(data.stride || []), newStrideItem.trim()];
                                        setData({...data, stride: newStride});
                                        setNewStrideItem("");
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
                         { Object.entries(data.references).map(([key, referenceUuid]) => {
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

export default withStyles(useStyles)(ManageThreats);