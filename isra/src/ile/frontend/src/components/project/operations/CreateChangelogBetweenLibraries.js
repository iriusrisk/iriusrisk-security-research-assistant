import React, { useState, useEffect } from 'react';
import { withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import Changelog from "./Changelog";
import { failedToast, successToast } from "../../utils/toastFunctions";
import Button from "@material-ui/core/Button";
import ReactToPrint from "react-to-print";
import Select from "@material-ui/core/Select";
import Paper from "@material-ui/core/Paper";
import InputLabel from "@material-ui/core/InputLabel";
import Grid from "@material-ui/core/Grid";

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

const CreateChangelogBetweenLibraries = (props) => {
    const { classes } = props;
    const [all, setAll] = useState([]);
    const [versions, setVersions] = useState([]);
    const [selectedVersionFirst, setSelectedVersionFirst] = useState("");
    const [selectedVersionSecond, setSelectedVersionSecond] = useState("");
    const [librariesFirst, setLibrariesFirst] = useState([]);
    const [selectedLibraryFirst, setSelectedLibraryFirst] = useState("");
    const [librariesSecond, setLibrariesSecond] = useState([]);
    const [selectedLibrarySecond, setSelectedLibrarySecond] = useState("");
    const [data, setData] = useState({"nodes":[], "links":[], "changelogList":[]});

    useEffect(() => {
        axios.get(`/project/report`)
            .then(res => {
                if(res.data.versionReports.length > 0){
                    let vers = [];
                    let map = {};
                    res.data.versionReports.forEach((version) => {
                        let list = [];
                        version.libraryReport.forEach((lib) => {
                            list.push(lib.libraryRef);
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
        let data = {
            "firstVersion": selectedVersionFirst,
            "firstLibrary": selectedLibraryFirst,
            "secondVersion": selectedVersionSecond,
            "secondLibrary": selectedLibrarySecond
        };

        axios.post('/project/diff/libraries', data)
            .then(res => {
                if(res.data.equalRevisionNumber){
                    failedToast("Libraries have the same revision number")
                }
                setData(res.data);
                successToast("Changelog generated");
            })
            .catch(err => failedToast("Changelog process failed: " + err));

        event.preventDefault();
    };

    return (
        <div className={classes.root}>
          <CssBaseline />
          <Container maxWidth="lg" className={classes.container}>
              <div>
                  <Typography variant="h4">
                      Create Changelog Between Libraries
                  </Typography>
                  <ReactToPrint
                      trigger={() => {return <Button variant="contained" color="primary">Export PDF</Button>;}}
                      content={() => this}
                  />
                  <div>
                      <Paper className={classes.paper} elevation={3}>
                          <Grid container>
                              <Grid item xs={3}>
                                  <InputLabel>
                                      Old version
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
                                      Old library
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
                                      New version
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
                                      New library
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
                          <Button variant="contained" color="primary" onClick={handleSubmit}>Submit</Button>
                      </Paper>
                  </div>
                  <Changelog data={data}/>
              </div>
          </Container>
        </div>
    );
};

export default withStyles(useStyles)(CreateChangelogBetweenLibraries);