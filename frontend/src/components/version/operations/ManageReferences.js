import React, { useState, useEffect, useCallback, useRef } from 'react';
import {withStyles} from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import MaterialTable from "material-table";
import {easyToast, failedToast, successToast} from "../../utils/toastFunctions";
import {excelDelimiter} from "../../utils/commonFunctions";

const useStyles = (theme) => ({
    root: {
      display: 'flex',
    },
    container: {
      paddingTop: theme.spacing(4),
      paddingBottom: theme.spacing(4),
    },
});

const ManageReferences = (props) => {
    const { classes, version: initialVersion } = props;
    const [version] = useState(initialVersion);
    const [data, setData] = useState([]);
    const dataRef = useRef([]);

    const addReference = useCallback((reference) => {
        axios.post('/api/version/'+version+'/reference', reference)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Add the returned object from the API to the state
                    setData(prevData => [...prevData, res.data]);
                    dataRef.current = [...dataRef.current, res.data];
                    easyToast(res, "Reference added", "Reference couldn't be added");
                }
            })
            .catch(err => failedToast(err));
    }, [version]);

    const updateReference = useCallback((updatedReference) => {
        axios.put('/api/version/'+version+'/reference', updatedReference)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Update the state with the returned object from the API
                    setData(prevData => {
                        const newData = prevData.map(item => 
                            item.uuid === updatedReference.uuid ? res.data : item
                        );
                        return newData;
                    });
                    dataRef.current = dataRef.current.map(item => 
                        item.uuid === updatedReference.uuid ? res.data : item
                    );
                    easyToast(res, "Reference updated", "Reference couldn't be updated");
                }
            })
            .catch(err => failedToast(err));
    }, [version]);

    const deleteReferences = useCallback((rowData) => {
        axios.delete('/api/version/'+version+'/reference', {data: rowData})
            .then(res => {
                if (res.status === 200) {
                    successToast("Reference/s deleted");
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
            .catch(err => failedToast("Reference/s couldn't be deleted: " + err));
    }, [version]);

    useEffect(() => {
        axios.get('/api/version/' + version + '/reference',)
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
                      Manage references
                  </Typography>
                  <MaterialTable
                      title="References"
                      columns={[
                      { title: 'Name', editable: 'always', field: 'name' },
                      { title: 'Url', editable: 'always', field: 'url' },
                      { title: 'UUID', field: 'uuid' },
                    ]}
                      data={data}
                      key="references-table"
                      options={{
                          selection: true,
                          sorting: true,
                          exportAllData: true,
                          exportDelimiter: excelDelimiter,
                          exportButton: true
                      }}
                      actions={[
                          {
                              tooltip: 'Remove All Selected References',
                              icon: 'delete',
                              onClick: (evt, rowData) => deleteReferences(rowData)
                          }
                      ]}
                      editable={{
                          onRowAdd: newData =>
                              new Promise((resolve) => {
                                  setTimeout(() => {
                                      addReference(newData);
                                      resolve();
                                  }, 100)
                              }),
                          onRowUpdate: (newData, oldData) =>
                              new Promise((resolve) => {
                                  setTimeout(() => {
                                      const updatedReference = {
                                          uuid: oldData.uuid,
                                          name: newData.name,
                                          url: newData.url
                                      };
                                      updateReference(updatedReference);
                                      resolve();
                                  }, 100)
                              }),
                          onRowDelete: oldData =>
                              new Promise((resolve) => {
                                  setTimeout(() => {
                                      deleteReferences([oldData]);
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

export default withStyles(useStyles)(ManageReferences);