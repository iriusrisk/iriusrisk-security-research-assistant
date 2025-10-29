import Container from '@material-ui/core/Container';
import CssBaseline from '@material-ui/core/CssBaseline';
import { makeStyles } from '@material-ui/core/styles';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import MaterialTable from "material-table";
import React, { useEffect, useState } from 'react';
import { excelDelimiter } from "../../utils/commonFunctions";
import { failedToast, successToast } from "../../utils/toastFunctions";

const useStyles = makeStyles((theme) => ({
    root: {
      display: 'flex',
    },
    container: {
      paddingTop: theme.spacing(4),
      paddingBottom: theme.spacing(4),
    },
}));

const ManageCategories = ({ version }) => {
    const classes = useStyles();
    const [data, setData] = useState([]);

    useEffect(() => {
        axios.get('/api/version/' + version + '/category')
            .then(res => {
                setData(res.data);
            })
            .catch(err => failedToast(err));
    }, [version]);

    const addCategory = (Category) => {
        axios.post('/api/version/' + version + '/category', Category)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Update the table with the returned category object
                    const newData = [...data, res.data];
                    setData(newData);
                    successToast("Category added");
                } else {
                    failedToast("Category couldn't be added");
                }
            })
            .catch(err => failedToast(err));
    };

    const updateCategory = (postdata) => {
        axios.put('/api/version/' + version + '/category', postdata)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Update the table with the returned category object
                    const dataUpdate = [...data];
                    const index = dataUpdate.findIndex(item => item.uuid === res.data.uuid);
                    if (index !== -1) {
                        dataUpdate[index] = res.data;
                        setData(dataUpdate);
                        successToast("Category updated");
                    }
                } else {
                    failedToast("Category couldn't be updated");
                }
            })
            .catch(err => failedToast(err));
    };

    const deleteCategories = (rowData) => {
        let _data = [...data];

        axios.delete('/api/version/' + version + '/category', { data: rowData })
            .then(res => {
                if (res.status === 200) {
                    successToast("Category/ies deleted");
                    rowData.forEach(rd => {
                        _data = _data.filter(t => t.tableData.id !== rd.tableData.id);
                    });
                    setData(_data);
                }
            })
            .catch(err => failedToast("Category/ies couldn't be deleted: " + err));
    };

    return (
        <div className={classes.root}>
            <CssBaseline />
            <Container maxWidth="lg" className={classes.container}>
                <div>
                    <Typography variant="h4">
                        Manage categories
                    </Typography>
                    <MaterialTable
                        title="Categories"
                        columns={[
                            { title: 'Ref', field: 'ref' },
                            { title: 'Name', field: 'name' },
                            { title: 'UUID', editable: false, field: 'uuid' }
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
                                tooltip: 'Remove All Selected Categories',
                                icon: 'delete',
                                onClick: (evt, data) => deleteCategories(data)
                            }
                        ]}
                        editable={{
                            onRowAdd: newData =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        addCategory(newData);
                                        resolve();
                                    }, 100)
                                }),
                            onRowUpdate: (newData, oldData) =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        // Validate required fields
                                        if (!oldData.uuid || !newData.ref || !newData.name) {
                                            failedToast("UUID, ref, and name are required fields");
                                            resolve();
                                            return;
                                        }
                                        
                                        const updatedCategory = {
                                            uuid: oldData.uuid,
                                            ref: newData.ref,
                                            name: newData.name
                                        };
                                        updateCategory(updatedCategory);
                                        resolve();
                                    }, 100)
                                }),
                            onRowDelete: oldData =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        deleteCategories([oldData]);
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

export default ManageCategories;