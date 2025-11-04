import React, { useState, useEffect } from 'react';
import { withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import { failedToast, successToast } from "../../utils/toastFunctions";
import ListItem from "@material-ui/core/ListItem";
import Grid from "@material-ui/core/Grid";
import List from "@material-ui/core/List";
import InputLabel from "@material-ui/core/InputLabel";
import Select from "@material-ui/core/Select";
import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import CircularProgress from "@material-ui/core/CircularProgress";

const useStyles = (theme) => ({
    root: {
        display: 'flex',
    },
    container: {
        paddingTop: theme.spacing(4),
        paddingBottom: theme.spacing(4),
    },
    newItem: {
        backgroundColor: "#13e29d"
    },
    deletedItem: {
        backgroundColor: "#f97678"
    },
    editedItem: {
        backgroundColor: "#ffe381"
    },
    paper:{
        padding: "20px",
        margin: "5px"
    }
});

const MergeLibraries = (props) => {
    const { classes } = props;
    const [all, setAll] = useState([]);
    const [versions, setVersions] = useState([]);
    const [selectedVersionFirst, setSelectedVersionFirst] = useState("");
    const [selectedVersionSecond, setSelectedVersionSecond] = useState("");
    const [librariesFirst, setLibrariesFirst] = useState([]);
    const [selectedLibraryFirst, setSelectedLibraryFirst] = useState("");
    const [librariesSecond, setLibrariesSecond] = useState([]);
    const [selectedLibrarySecond, setSelectedLibrarySecond] = useState("");
    const [data, setData] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);

    useEffect(() => {
        axios.get(`/api/project/report`)
            .then(res => {
                if(res.data.version_reports.length > 0){
                    let vers = [];
                    let map = {};
                    res.data.version_reports.forEach((version) => {
                        let list = [];
                        version.library_reports.forEach((lib) => {
                            list.push(lib.library_ref);
                        });
                        vers.push(version.version);
                        map[version.version] = list;
                    });

                    setVersions(vers);
                    setAll(map);
                    setLibrariesFirst(map[Object.keys(map)[0]]);
                    setLibrariesSecond(map[Object.keys(map)[0]]);
                    setSelectedVersionFirst(Object.keys(map)[0]);
                    setSelectedVersionSecond(Object.keys(map)[0]);
                    setSelectedLibraryFirst(map[Object.keys(map)[0]][0]);
                    setSelectedLibrarySecond(map[Object.keys(map)[0]][0]);
                }
            })
            .catch(err => failedToast(err));
    }, []);

    const handleChangeVersionFirst = (event) => {
        let lib = "";
        if(all[event.target.value].length > 0){
            lib = all[event.target.value][0];
        }
        setSelectedVersionFirst(event.target.value);
        setLibrariesFirst(all[event.target.value]);
        setSelectedLibraryFirst(lib);
    };

    const handleChangeVersionSecond = (event) => {
        let lib = "";
        if(all[event.target.value].length > 0){
            lib = all[event.target.value][0];
        }
        setSelectedVersionSecond(event.target.value);
        setLibrariesSecond(all[event.target.value]);
        setSelectedLibrarySecond(lib);
    };

    const handleChangeLibraryFirst = (event) => {
        setSelectedLibraryFirst(event.target.value);
    };

    const handleChangeLibrarySecond = (event) => {
        setSelectedLibrarySecond(event.target.value);
    };

    const handleSubmit = (event) => {
        setIsLoading(true);
        let data = {
            "src_version": selectedVersionFirst,
            "src_library": selectedLibraryFirst,
            "dst_version": selectedVersionSecond,
            "dst_library": selectedLibrarySecond
        };

        axios.post('/api/project/mergeLibraries', data)
            .then(res => {
                if(res.data.length === 0){
                    successToast("Nothing to merge");
                }else{
                    successToast("Merge successful");
                }
                setData(res.data);
                setIsLoading(false);
            })
            .catch(err => {
                failedToast("Merge process failed: " + err);
                setIsLoading(false);
            });

        event.preventDefault();
    };

    const handleSubmitGenerateFullLibrary = (event) => {
        setIsGenerating(true);
        let data = {
            "src_version": selectedVersionFirst
        };

        axios.post('/api/project/generateFullLibrary', data)
            .then(res => {
                successToast("Generated. Reload and check full_version");
                setIsGenerating(false);
            })
            .catch(err => {
                failedToast("Generate process failed: " + err);
                setIsGenerating(false);
            });

        event.preventDefault();
    };

    return (
        <div className={classes.root}>
            <CssBaseline />
            <Container maxWidth="lg" className={classes.container}>
                <div>
                    <Typography variant="h4">
                        Merge Libraries
                    </Typography>
                    <Typography variant="body1">
                        This process will copy all new elements from the source library to the target library. It will also update standards and references if the elements already exist in the target version.
                    </Typography>
                    <div>
                        <Paper className={classes.paper} elevation={3}>
                            <Grid container>
                                <Grid item xs={3}>
                                    <InputLabel>
                                        Source version
                                    </InputLabel>
                                    <Select
                                        native
                                        value={selectedVersionFirst}
                                        variant="outlined"
                                        classes={classes.select}
                                        onChange={(event) => handleChangeVersionFirst(event)}
                                    >
                                        {versions.map((value, index) => {
                                            return <option key={index} value={value}>{value}</option>
                                        })}
                                    </Select>

                                </Grid>
                                <Grid item xs={9}>
                                    <InputLabel>
                                        Source library
                                    </InputLabel>
                                    <Select
                                        native
                                        value={selectedLibraryFirst}
                                        variant="outlined"
                                        onChange={(event) => handleChangeLibraryFirst(event)}
                                    >
                                        {librariesFirst.map((value, index) => {
                                            return <option key={index} value={value}>{value}</option>
                                        })}
                                    </Select>
                                </Grid>
                            </Grid>
                            <Grid container>
                                <Grid item xs={3}>
                                    <InputLabel>
                                        Target version
                                    </InputLabel>
                                    <Select
                                        native
                                        value={selectedVersionSecond}
                                        variant="outlined"
                                        onChange={(event) => handleChangeVersionSecond(event)}
                                    >
                                        {versions.map((value, index) => {
                                            return <option key={index} value={value}>{value}</option>
                                        })}
                                    </Select>
                                </Grid>
                                <Grid item xs={9}>
                                    <InputLabel>
                                        Target library
                                    </InputLabel>
                                    <Select
                                        native
                                        value={selectedLibrarySecond}
                                        variant="outlined"
                                        onChange={(event) => handleChangeLibrarySecond(event)}
                                    >
                                        {librariesSecond.map((value, index) => {
                                            return <option key={index} value={value}>{value}</option>
                                        })}
                                    </Select>
                                </Grid>
                            </Grid>
                            <Button 
                                variant="contained" 
                                color="primary" 
                                onClick={handleSubmit}
                                disabled={isLoading}
                            >
                                {isLoading ? (
                                    <>
                                        <CircularProgress size={20} style={{ marginRight: 8, color: 'white' }} />
                                        Merging...
                                    </>
                                ) : (
                                    'Submit'
                                )}
                            </Button>
                            <Button 
                                variant="contained" 
                                color="primary" 
                                onClick={handleSubmitGenerateFullLibrary}
                                disabled={isGenerating}
                                style={{ marginLeft: 8 }}
                            >
                                {isGenerating ? (
                                    <>
                                        <CircularProgress size={20} style={{ marginRight: 8, color: 'white' }} />
                                        Generating...
                                    </>
                                ) : (
                                    'Generate a single library with the content of the source version'
                                )}
                            </Button>
                        </Paper>
                    </div>
                    <List>
                        {data.map((value, index) => {
                            let color = classes.newItem;

                            return <ListItem key={index} className={color}>
                                <Grid container spacing={3}>
                                    <Grid item xs={12}>
                                        <Typography>
                                            {value}
                                        </Typography>
                                    </Grid>
                                </Grid>
                            </ListItem>
                        })}
                    </List>
                </div>
            </Container>
        </div>
    );
};

export default withStyles(useStyles)(MergeLibraries);