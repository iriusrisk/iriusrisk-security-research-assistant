import InlineEditor from '@ckeditor/ckeditor5-build-inline';
import CKEditor from '@ckeditor/ckeditor5-react';
import Button from "@material-ui/core/Button";
import Container from '@material-ui/core/Container';
import CssBaseline from '@material-ui/core/CssBaseline';
import { makeStyles } from '@material-ui/core/styles';
import TextField from "@material-ui/core/TextField";
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import MaterialTable from "material-table";
import React, { useState, useEffect } from 'react';
import { excelDelimiter } from "../../utils/commonFunctions";
import { easyToast, failedToast, successToast } from "../../utils/toastFunctions";

const useStyles = makeStyles((theme) => ({
    root: {
      display: 'flex',
    },
    container: {
      paddingTop: theme.spacing(4),
      paddingBottom: theme.spacing(4),
    },
    paper: {
        border: "10px",
        borderColor: "blue"
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

const ManageRiskPatterns = (props) => {
    const classes = useStyles();
    const { match } = props;
    
    const [version, setVersion] = useState(match.params.id);
    const [library, setLibrary] = useState(match.params.lib);
    const [data, setData] = useState([]);

    useEffect(() => {
        axios.get('/api/version/' + version + '/' + library + '/riskPattern')
            .then(res => {
                setData(res.data);
            })
            .catch(err => failedToast(err));
    }, [version, library]);

    const addRiskPattern = (RiskPattern) => {
        // Structure the data according to RiskPatternRequest model
        const requestData = {
            ref: RiskPattern.ref || "",
            name: RiskPattern.name || "",
            desc: RiskPattern.desc || ""
        };

        axios.post('/api/version/' + version + '/' + library + '/riskPattern', requestData)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Update the table with the returned risk pattern object
                    const newData = [...data, res.data];
                    setData(newData);
                    successToast("RiskPattern added");
                } else {
                    failedToast("RiskPattern couldn't be added");
                }
            })
            .catch(err => failedToast(err));
    };

    const deleteRiskPatterns = (rowData) => {
        let _data = [...data];

        axios.delete('/api/version/' + version + '/' + library + '/riskPattern', {data: rowData})
            .then(res => {
                if(res.status === 200){
                    successToast("Risk pattern/s deleted");
                    rowData.forEach(rd => {
                        _data = _data.filter(t => t.tableData.id !== rd.tableData.id);
                    });
                    setData(_data);
                }
            })
            .catch(err => failedToast("Risk pattern/s couldn't be deleted: " + err));
    };

    return (
        <div className={classes.root}>
            <CssBaseline />
            <Container maxWidth="lg" className={classes.container}>
                <div>
                    <Typography variant="h4">
                        Manage risk patterns
                    </Typography>
                    <MaterialTable
                        title="RiskPatterns"
                        columns={[
                            { title: 'Ref', editable: 'onAdd', field: 'ref' },
                            { title: 'Name', field: 'name' },
                            ]}
                        data={data}
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
                                tooltip: 'Remove All Selected RiskPatterns',
                                icon: 'delete',
                                onClick: (evt, data) => deleteRiskPatterns(data)
                            }
                        ]}
                        detailPanel={rowData => {
                            return (
                                <RiskPatternDetailPanel version={version} library={library} rowData={rowData} />
                            )
                        }}
                        editable={{
                            onRowAdd: newData =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        const riskPatternData = {
                                            ref: newData.ref || "",
                                            name: newData.name || "",
                                            desc: ""
                                        };
                                        addRiskPattern(riskPatternData);
                                        resolve();
                                    }, 100)
                                }),
                            onRowDelete: oldData =>
                                new Promise((resolve) => {
                                    setTimeout(() => {
                                        deleteRiskPatterns([oldData]);
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

const RiskPatternDetailPanel = (props) => {
    const { version, library, rowData } = props;
    
    const [data, setData] = useState(rowData);
    const [suggestions, setSuggestions] = useState([]);

    const updateRiskPatternBody = (event) => {
        // Structure the data according to RiskPatternRequest model
        const requestData = {
            uuid: event.target.uuid.value || "",
            ref: event.target.ref.value || "",
            name: event.target.name.value || "",
            desc: data.desc || ""
        };

        axios.put('/api/version/' + version + '/' + library + '/riskPattern', requestData)
            .then(res => {
                easyToast(res, "RiskPattern update", "RiskPattern couldn't be updated");
            })
            .catch(err => failedToast(err));
        event.preventDefault();
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
            <form style={classes.form} onSubmit={updateRiskPatternBody}>
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="ref"
                    label="RiskPattern ref"
                    defaultValue={data.ref}
                    autoFocus
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="name"
                    label="RiskPattern name"
                    defaultValue={data.name}
                />
                <TextField
                    variant="outlined"
                    margin="normal"
                    fullWidth
                    id="uuid"
                    label="UUID"
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
};

export default ManageRiskPatterns;