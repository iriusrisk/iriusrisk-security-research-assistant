import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import { easyToast, failedToast, successToast } from "../../utils/toastFunctions";
import MaterialTable from "material-table";
import Grid from "@material-ui/core/Grid";
import Button from "@material-ui/core/Button";
import FormControl from "@material-ui/core/FormControl";
import InputLabel from "@material-ui/core/InputLabel";
import Select from "@material-ui/core/Select";
import ClearIcon from '@material-ui/icons/Clear';
import { excelDelimiter } from "../../utils/commonFunctions";

const useStyles = makeStyles((theme) => ({
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
}));

const ManageComponents = (props) => {
    const classes = useStyles();
    const { match } = props;
    
    const [version, setVersion] = useState(match.params.id);
    const [library, setLibrary] = useState(match.params.lib);
    const [data, setData] = useState([]);
    const [suggestions, setSuggestions] = useState([]);

    useEffect(() => {
        axios.get('/api/version/' + version + '/' + library + '/component')
            .then(res => {
                setData(res.data);
            })
            .catch(err => failedToast(err));

        axios.get('/api/version/' + version + '/' + library + '/riskPattern')
            .then(res => {
                setSuggestions(res.data);
            })
            .catch(err => failedToast(err));
    }, [version, library]);

    const addComponent = (Component) => {
        return axios.post('/api/version/' + version + '/' + library + '/component', Component)
            .then(res => {
                easyToast(res, "Component added", "Component couldn't be added");
                return res.data; // Return the created component data
            })
            .catch(err => {
                failedToast(err);
                throw err;
            });
    };

    const updateComponent = (newComponent) => {
        let postdata = {
            uuid: newComponent.uuid,
            ref: newComponent.ref,
            name: newComponent.name,
            desc: newComponent.desc,
            category_ref: newComponent.category_ref,
            visible: newComponent.visible,
            risk_pattern_refs: newComponent.risk_pattern_refs || []
        };

        return axios.put('/api/version/' + version + '/' + library + '/component', postdata)
            .then(res => {
                easyToast(res, "Component updated", "Component couldn't be updated");
                return res.data; // Return the updated component data
            })
            .catch(err => {
                failedToast(err);
                throw err;
            });
    };

    const deleteComponents = (rowData) => {
        let _data = [...data];

        axios.delete('/api/version/' + version + '/' + library + '/component', {data: rowData})
            .then(res => {
                if(res.status === 200){
                    successToast("Component/s deleted");
                    rowData.forEach(rd => {
                        _data = _data.filter(t => t.tableData.id !== rd.tableData.id);
                    });
                    setData(_data);
                }
            })
            .catch(err => failedToast("Component/s couldn't be deleted: " + err));
    };

    const addRiskPattern = (id, event) => {
        const dataAdd = [...data];
        const index = dataAdd[id].risk_pattern_refs.indexOf(event.target.value);
        if (index === -1) {
            dataAdd[id].risk_pattern_refs.push(event.target.value);
            updateComponent(dataAdd[id])
                .then(updatedComponent => {
                    const updatedData = [...data];
                    updatedData[id] = updatedComponent;
                    setData(updatedData);
                })
                .catch(err => {
                    const revertedData = [...data];
                    setData(revertedData);
                });
        } else {
            failedToast("Risk pattern " + event.target.value + " already exists in this component")
        }
    };

    const deleteRiskPattern = (id, value) => {
        const dataDelete = [...data];
        const index = dataDelete[id].risk_pattern_refs.indexOf(value);
        if (index > -1) {
            dataDelete[id].risk_pattern_refs.splice(index, 1);
            updateComponent(dataDelete[id])
                .then(updatedComponent => {
                    const updatedData = [...data];
                    updatedData[id] = updatedComponent;
                    setData(updatedData);
                })
                .catch(err => {
                    const revertedData = [...data];
                    setData(revertedData);
                });
        }
    };

    const tags = (rowData, classes) => {
        if(!rowData.hasOwnProperty("risk_pattern_refs")){
            rowData.risk_pattern_refs = [];
        }
        return (
            <Grid>
                {rowData.risk_pattern_refs.length > 0 &&
                    <div>
                    { rowData.risk_pattern_refs.map((value, index) => {
                     return <Button variant="outlined" startIcon={<ClearIcon />} className={classes.redHover} key={index} onClick={() => deleteRiskPattern(rowData.tableData.id, value)}>{value}</Button>
                    })}
                    </div>
                }
                <FormControl variant="filled" className={classes.formControl}>
                    <InputLabel htmlFor="outlined-age-native-simple">Add risk pattern</InputLabel>
                    <Select
                        native
                        value=""
                        onChange={(event) => addRiskPattern(rowData.tableData.id, event)}
                    >
                        <option key={2345678} disabled value=""> </option>
                        {suggestions.map((value, index) => {
                          return <option key={index} value={value.ref}>{value.name}</option>
                        })}
                    </Select>
                </FormControl>
            </Grid>
        );
    };

    return (
        <div className={classes.root}>
            <CssBaseline />
            <Container maxWidth="lg" className={classes.container}>
                <div>
                    <Typography variant="h4">
                        Manage components
                    </Typography>
                    <MaterialTable
                        title="Components"
                        columns={[
                            { title: 'Ref', editable: 'onAdd', field: 'ref' },
                            { title: 'Name', field: 'name' },
                            { title: 'Desc', field: 'desc' },
                            { title: 'Category', field: 'category_ref' },
                            { title: 'Risk patterns', emptyValue:[], editable: 'never', field: 'risk_pattern_refs', render: rowData => {
                                    return tags(rowData, classes);
                            }},
                            { title: 'Visible', field: 'visible' },
                            { title: 'UUID', field: 'uuid' },
                            ]}
                        data={data}
                        options={{
                            selection: true,
                            sorting: true,
                            exportAllData: true,
                            exportDelimiter: excelDelimiter,
                            exportButton: true
                        }}
                        actions={[
                            {
                                tooltip: 'Remove All Selected Components',
                                icon: 'delete',
                                onClick: (evt, data) => deleteComponents(data)
                            }
                        ]}
                        editable={{
                            onRowAdd: newData =>
                                new Promise((resolve, reject) => {
                                    setTimeout(() => {
                                        newData.risk_pattern_refs = [];
                                        addComponent(newData)
                                            .then(createdComponent => {
                                                setData([...data, createdComponent]);
                                                resolve();
                                            })
                                            .catch(err => {
                                                reject();
                                            });
                                    }, 100)
                                }),
                            onRowUpdate: (newData, oldData) =>
                                new Promise((resolve, reject) => {
                                    setTimeout(() => {
                                        updateComponent(newData)
                                            .then(updatedComponent => {
                                                const dataUpdate = [...data];
                                                const index = oldData.tableData.id;
                                                dataUpdate[index] = updatedComponent;
                                                setData([...dataUpdate]);
                                                resolve();
                                            })
                                            .catch(err => {
                                                reject();
                                            });
                                    }, 100)
                                }),
                            onRowDelete: oldData =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        deleteComponents([oldData]);
                                        resolve()
                                    }, 100)
                                }),
                        }}
                    />
                </div>
            </Container>
        </div>
    );
};

export default ManageComponents;