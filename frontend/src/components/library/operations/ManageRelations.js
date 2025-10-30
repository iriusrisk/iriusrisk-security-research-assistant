import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import { failedToast, successToast } from "../../utils/toastFunctions";
import MaterialTable from "material-table";
import { excelDelimiter, sortArrayByKey } from "../../utils/commonFunctions";
import Select from "@material-ui/core/Select";
import FormControl from "@material-ui/core/FormControl";
import InputLabel from "@material-ui/core/InputLabel";

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

const ManageRelations = (props) => {
    const classes = useStyles();
    const { match } = props;
    
    const version = match.params.id;
    const library = match.params.lib;
    const [rps, setRps] = useState([]);
    const [selectedRp, setSelectedRp] = useState("");
    const [data, setData] = useState([]);

    useEffect(() => {
        axios.get('/api/version/' + version + '/' + library + '/riskPattern')
            .then(res => {
                setRps(sortArrayByKey(res.data, "ref"));
            })
            .catch(err => failedToast(err));
    }, [version, library]);

    const updateTable = (value) => {
        axios.get('/api/version/' + version + '/' + library + '/relation')
            .then(res => {
                setSelectedRp(value);
                // Filter relations for the selected risk pattern
                const filteredData = res.data.filter(relation => relation.risk_pattern_uuid === value);
                setData(filteredData);
            })
            .catch(err => failedToast(err));
    };

    const selectRp = (event) => {
        let value = event.target.value;
        updateTable(value);
    };

    const addRelation = (newData) => {
        const relation = {
            risk_pattern_uuid: selectedRp,
            usecase_uuid: newData.usecase_uuid || "",
            threat_uuid: newData.threat_uuid || "",
            weakness_uuid: newData.weakness_uuid || "",
            control_uuid: newData.control_uuid || "",
            mitigation: newData.mitigation || "100"
        };

        axios.post('/api/version/' + version + '/' + library + '/relation', relation)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Update the table with the returned relation object
                    const newDataArray = [...data, res.data];
                    setData(newDataArray);
                    successToast("Relation added");
                } else {
                    failedToast("Relation couldn't be added");
                }
            })
            .catch(err => failedToast("Relation couldn't be added: " + err));
    };

    const updateRelation = (oldData, newData) => {
        const updatedRelation = {
            uuid: newData.uuid,
            risk_pattern_uuid: selectedRp,
            usecase_uuid: newData.usecase_uuid || "",
            threat_uuid: newData.threat_uuid || "",
            weakness_uuid: newData.weakness_uuid || "",
            control_uuid: newData.control_uuid || "",
            mitigation: newData.mitigation || "100"
        };

        axios.put('/api/version/' + version + '/' + library + '/relation', updatedRelation)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Update the table with the returned relation object
                    const dataUpdate = [...data];
                    const index = dataUpdate.findIndex(item => item.uuid === res.data.uuid);
                    if (index !== -1) {
                        dataUpdate[index] = res.data;
                        setData(dataUpdate);
                        successToast("Relation updated");
                    }
                } else {
                    failedToast("Relation couldn't be updated");
                }
            })
            .catch(err => failedToast("Relation couldn't be updated: " + err));
    };

    const deleteRelations = (rowData) => {
        let _data = [...data];

        for(const r of rowData){
            r["risk_pattern_uuid"] = selectedRp;
        }

        axios.delete('/api/version/' + version + '/' + library + '/relation', {data: rowData})
            .then(res => {
                if(res.status === 200){
                    successToast("Relation/s deleted");
                    rowData.forEach(rd => {
                        _data = _data.filter(t => t.uuid !== rd.uuid);
                    });
                    setData(_data);
                }
            })
            .catch(err => failedToast("Relation/s couldn't be deleted: " + err));
    };

    return (
        <div className={classes.root}>
            <CssBaseline />
            <Container maxWidth="lg" className={classes.container}>
                <div>
                    <Typography variant="h4">
                        Manage relations
                    </Typography>
                    <FormControl className={classes.formControl}>
                        <InputLabel>Select Risk Pattern</InputLabel>
                        <Select
                            native
                            value={selectedRp}
                            onChange={(event) => selectRp(event)}
                        >
                            <option key={2345678} value="">Select a risk pattern</option>
                            { rps.map((value, index) => {
                                return <option key={index} value={value.uuid}>{value.ref} - {value.name}</option>
                            })}
                        </Select>
                    </FormControl>
                    { selectedRp !== "" &&
                    <div>
                      <MaterialTable
                        title={`Relations for ${rps.find(rp => rp.uuid === selectedRp)?.ref || selectedRp}`}
                        columns={[
                            { 
                                title: 'Usecase UUID', 
                                field: 'usecase_uuid',
                                editable: 'always'
                            },
                            { 
                                title: 'Threat UUID', 
                                field: 'threat_uuid',
                                editable: 'always'
                            },
                            { 
                                title: 'Weakness UUID', 
                                field: 'weakness_uuid',
                                editable: 'always'
                            },
                            { 
                                title: 'Control UUID', 
                                field: 'control_uuid',
                                editable: 'always'
                            },
                            { 
                                title: 'Mitigation', 
                                field: 'mitigation',
                                editable: 'always'
                            },
                        ]}
                        data={data}
                        options={{
                            selection: true,
                            sorting: true,
                            search: true,
                            exportAllData: true,
                            exportDelimiter: excelDelimiter,
                            exportButton: true,
                            grouping: true,
                            pageSize: 10,
                            pageSizeOptions: [10, 20, 50]
                        }}
                        actions={[
                            {
                                tooltip: 'Remove All Selected Relations',
                                icon: 'delete',
                                onClick: (evt, data) => deleteRelations(data)
                            }
                        ]}
                        editable={{
                            onRowAdd: newData =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        addRelation(newData);
                                        resolve();
                                    }, 100)
                                }),
                            onRowUpdate: (newData, oldData) =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        updateRelation(oldData, newData);
                                        resolve();
                                    }, 100)
                                }),
                            onRowDelete: oldData =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        deleteRelations([oldData]);
                                        resolve()
                                    }, 100)
                                }),
                        }}
                      />
                    </div>
                    }
                </div>
            </Container>
        </div>
    );
};

export default ManageRelations;