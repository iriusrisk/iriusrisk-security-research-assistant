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
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import {excelDelimiter} from "../../utils/commonFunctions";

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

const ManageUsecases = (props) => {
    const { classes, version: initialVersion } = props;
    const [version] = useState(initialVersion);
    const [data, setData] = useState([]);
    const dataRef = useRef([]);

    const addUsecase = useCallback((usecase) => {
        axios.post('/version/'+version+'/usecase', usecase)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Add the returned object from the API to the state
                    setData(prevData => [...prevData, res.data]);
                    dataRef.current = [...dataRef.current, res.data];
                    easyToast(res, "Usecase added", "Usecase couldn't be added");
                }
            })
            .catch(err => {
                failedToast(err);
            });
    }, [version]);

    const updateUsecase = useCallback((updatedUsecase) => {
        axios.put('/version/'+version+'/usecase', updatedUsecase)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Update the state with the returned object from the API
                    setData(prevData => {
                        const newData = prevData.map(item => 
                            item.uuid === updatedUsecase.uuid ? res.data : item
                        );
                        return newData;
                    });
                    dataRef.current = dataRef.current.map(item => 
                        item.uuid === updatedUsecase.uuid ? res.data : item
                    );
                    easyToast(res, "Usecase updated", "Usecase couldn't be updated");
                }
            })
            .catch(err => failedToast(err));
    }, [version]);

    const updateUsecaseSilent = useCallback((updatedUsecase) => {
        // Update the ref without triggering a re-render
        dataRef.current = dataRef.current.map(item => 
            item.uuid === updatedUsecase.uuid ? updatedUsecase : item
        );
    }, []);

    const deleteUsecases = useCallback((rowData) => {
        axios.delete('/version/'+version+'/usecase', {data: rowData})
            .then(res => {
                if (res.status === 200) {
                    successToast("Usecase/s deleted");
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
            .catch(err => failedToast("Usecase/s couldn't be deleted: " + err));
    }, [version]);

    useEffect(() => {
        axios.get('/version/' + version + '/usecase',)
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
                        Manage usecases
                    </Typography>
                    <MaterialTable
                        title="Usecases"
                        columns={[
                            { title: 'Ref', editable: 'onAdd', field: 'ref' },
                            { title: 'Name', editable: 'always', field: 'name' }
                            ]}
                        data={data}
                        key="usecases-table"
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
                                tooltip: 'Remove All Selected Usecases',
                                icon: 'delete',
                                onClick: (evt, rowData) => deleteUsecases(rowData)
                            }
                        ]}
                        detailPanel={rowData => {
                            return (
                                <UsecaseDetailPanel 
                                    version={version} 
                                    rowData={rowData} 
                                    onUpdate={updateUsecaseSilent}
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
                                        addUsecase(newData);
                                        resolve();
                                    }, 100)
                                }),
                            onRowUpdate: (newData, oldData) =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        const updatedUsecase = {
                                            uuid: oldData.uuid,
                                            ref: newData.ref,
                                            name: newData.name,
                                            desc: oldData.desc || ""
                                        };
                                        updateUsecase(updatedUsecase);
                                        resolve();
                                    }, 100)
                                }),
                            onRowDelete: oldData =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        deleteUsecases([oldData]);
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

const UsecaseDetailPanel = (props) => {
    const { version, rowData: initialRowData, onUpdate } = props;
    const [data, setData] = useState(initialRowData);

    const updateUsecaseBody = (event) => {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const postdata = {
            uuid: formData.get('uuid') || "",
            ref: formData.get('ref') || "",
            name: formData.get('name') || "",
            desc: data.desc || "",
        };

        axios.put('/version/'+version+'/usecase', postdata)
            .then(res => {
                if (res.status === 200 && res.data) {
                    setData(res.data);
                    if (onUpdate) {
                        onUpdate(res.data);
                    }
                    easyToast(res, "Usecase updated", "Usecase couldn't be updated");
                }
            })
            .catch(err => {
                console.error('Error updating usecase:', err);
                failedToast(err);
            });
    };

    const handleDescChangeEditor = (data) => {
        let newData = {...data};
        newData.desc = data;
        setData(newData);
    };
    
    const classes = {
        form: {
            paddingLeft: "24px",
            paddingRight: "24px",
            backgroundColor: "#e1f0ff"
        }
    };

    return(
        <div>
            <form style={classes.form} onSubmit={updateUsecaseBody}>
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="ref"
                    name="ref"
                    label="Usecase ref"
                    defaultValue={data.ref}
                    autoFocus
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="name"
                    name="name"
                    label="Usecase name"
                    defaultValue={data.name}
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="uuid"
                    name="uuid"
                    label="Usecase uuid"
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

export default withStyles(useStyles)(ManageUsecases);