import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import { failedToast, successToast } from "../../utils/toastFunctions";
import MaterialTable from "material-table";
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
    },
    columns: {
        columnCount: 2
    }
}));

const ManageStandards = ({ version }) => {
    const classes = useStyles();
    const [data, setData] = useState([]);
    
    useEffect(() => {
        axios.get('/api/version/' + version + '/standard')
            .then(res => {
                setData(res.data);
            })
            .catch(err => failedToast(err));
    }, [version]);

    const addStandard = (standard) => {
        axios.post('/api/version/' + version + '/standard', standard)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Update the table with the returned standard object
                    const newData = [...data, res.data];
                    setData(newData);
                    successToast("Standard added");
                } else {
                    failedToast("Standard couldn't be added");
                }
            })
            .catch(err => failedToast(err));
    };

    const updateStandard = (postdata) => {
        axios.put('/api/version/' + version + '/standard', postdata)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Update the table with the returned standard object
                    const dataUpdate = [...data];
                    const index = dataUpdate.findIndex(item => item.uuid === res.data.uuid);
                    if (index !== -1) {
                        dataUpdate[index] = res.data;
                        setData(dataUpdate);
                        successToast("Standard updated");
                    }
                } else {
                    failedToast("Standard couldn't be updated");
                }
            })
            .catch(err => failedToast(err));
    };

    const deleteStandards = (rowData) => {
        let _data = [...data];

        axios.delete('/api/version/' + version + '/standard', { data: rowData })
            .then(res => {
                if (res.status === 200) {
                    successToast("Standard/s deleted");
                    rowData.forEach(rd => {
                        _data = _data.filter(t => t.tableData.id !== rd.tableData.id);
                    });
                    setData(_data);
                }
            })
            .catch(err => failedToast("Standard/s couldn't be deleted: " + err));
    };

    return (
        <div className={classes.root}>
            <CssBaseline />
            <Container maxWidth="lg" className={classes.container}>
                <Typography variant="h4">
                    Manage standards
                </Typography>
                <MaterialTable
                    title="Standards"
                    columns={[
                        { title: 'Supported standard ref', field: 'supported_standard_ref' },
                        { title: 'Standard ref', field: 'standard_ref' },
                        { title: 'UUID', editable: false, field: 'uuid' }
                    ]}
                    data={data}
                    options={{
                        selection: true,
                        sorting: true,
                        search: true,
                        exportAllData: true,
                        exportDelimiter: excelDelimiter,
                        exportButton: true,
                        grouping: true
                    }}
                    actions={[
                        {
                            tooltip: 'Remove All Selected standards',
                            icon: 'delete',
                            onClick: (evt, data) => deleteStandards(data)
                        }
                    ]}
                    editable={{
                        onRowAdd: newData =>
                            new Promise((resolve) => {
                                setTimeout(() => {
                                    addStandard(newData);
                                    resolve();
                                }, 100)
                            }),
                        onRowUpdate: (newData, oldData) =>
                            new Promise((resolve) => {
                                setTimeout(() => {
                                    // Validate required fields
                                    if (!oldData.uuid || !newData.supported_standard_ref || !newData.standard_ref) {
                                        failedToast("UUID, supported standard ref, and standard ref are required fields");
                                        resolve();
                                        return;
                                    }
                                    
                                    const updatedStandard = {
                                        uuid: oldData.uuid,
                                        supported_standard_ref: newData.supported_standard_ref,
                                        standard_ref: newData.standard_ref
                                    };
                                    updateStandard(updatedStandard);
                                    resolve();
                                }, 100)
                            }),
                        onRowDelete: oldData =>
                            new Promise((resolve) => {
                                setTimeout(() => {
                                    deleteStandards([oldData]);
                                    resolve()
                                }, 100)
                            }),
                    }}
                />
            </Container>
        </div>
    );
};

export default ManageStandards;