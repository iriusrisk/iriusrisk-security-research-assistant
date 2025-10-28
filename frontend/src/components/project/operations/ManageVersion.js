import React, { useState, useEffect } from 'react';
import { withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import { easyToast, failedToast } from "../../utils/toastFunctions";
import Grid from "@material-ui/core/Grid";
import Paper from "@material-ui/core/Paper";
import Button from "@material-ui/core/Button";
import Select from "@material-ui/core/Select";
import TextField from "@material-ui/core/TextField";

const useStyles = (theme) => ({
    root: {
      display: 'flex',
    },
    container: {
      paddingTop: theme.spacing(4),
      paddingBottom: theme.spacing(4),
    },
    paper:{
        padding: "20px",
        margin: "5px"
    },
    button: {
        float: "right"
    }
});

const ManageVersion = (props) => {
    const { classes, handleProjectChange } = props;
    const [ref, setRef] = useState("");
    const [versions, setVersions] = useState([]);
    const [selectedVersionFirst, setSelectedVersionFirst] = useState("");
    const [versionFiles, setVersionFiles] = useState([]);
    const [selectedVersionFile, setSelectedVersionFile] = useState("");

    useEffect(() => {
        axios.get('/project/versions')
            .then(res => {
                if(res.data.versions.length > 0){
                    setVersions(res.data.versions);
                    setSelectedVersionFirst(res.data.versions[0]);
                }
            })
            .catch(err => failedToast(err));

        axios.get('/version/list')
            .then(res => {
                if(res.status === 200){
                    if(res.data.length !== 0){
                        setVersionFiles(res.data);
                        setSelectedVersionFile(res.data[0]);
                    }
                }else{
                    failedToast("Failed to retrieve versions");
                }
            })
            .catch(err => failedToast("Failed to retrieve versions: " + err));
    }, []);

    const handleChangeVersionFirst = (event) => {
        setSelectedVersionFirst(event.target.value);
    };

    const handleChangeVersionFile = (event) => {
        setSelectedVersionFile(event.target.value);
    };

    const handleSubmit = (event) => {
        axios.post('/project/version/' + ref)
            .then(res => {
                easyToast(res, "Version created successfully", "Creating version failed");
                //props.handleVersionChange()
                if(res.status === 200){
                    handleProjectChange(res.data.project, res.data.versions);
                    if(res.data.versions.length > 0){
                        setVersions(res.data.versions);
                        setSelectedVersionFirst(res.data.versions[0]);
                    }else{
                        setVersions(res.data.versions);
                        setSelectedVersionFirst("");
                    }
                }
            })
            .catch(err => failedToast("Creating version failed: " + err));

        event.preventDefault();
    };

    const handleSubmitDelete = (event) => {
        axios.delete('/project/version/' + selectedVersionFirst)
            .then(res => {
                easyToast(res, "Version deleted successfully", "Deleting version failed");
                if(res.status === 200){
                    handleProjectChange(res.data.project, res.data.versions);
                    if(res.data.versions.length > 0){
                        setVersions(res.data.versions);
                        setSelectedVersionFirst(res.data.versions[0]);
                    }else{
                        setVersions(res.data.versions);
                        setSelectedVersionFirst("");
                    }
                }
            })
            .catch(err => failedToast("Deleting version failed: " + err));

        event.preventDefault();
    };

    const handleSubmitCopy = (event) => {
        let postData = {
            "srcVersion": selectedVersionFirst,
            "ref": ref
        };
        axios.post('/project/version/copy', postData)
            .then(res => {
                easyToast(res, "Version copied successfully", "Copying version failed");
                if(res.status === 200){
                    handleProjectChange(res.data.project, res.data.versions);
                    if(res.data.versions.length > 0){
                        setVersions(res.data.versions);
                        setSelectedVersionFirst(res.data.versions[0]);
                    }else{
                        setVersions(res.data.versions);
                        setSelectedVersionFirst("");
                    }
                }
            })
            .catch(err => failedToast("Copying version failed: " + err));

        event.preventDefault();
    };

    const handleSubmitLoad = (event) => {
        axios.get('/project/version/load/' + selectedVersionFile)
            .then(res => {
                easyToast(res, "Version loaded successfully", "Loading version failed");
                if(res.status === 200){
                    handleProjectChange(res.data.project, res.data.versions)
                }
            })
            .catch(err => failedToast("Loading version failed: " + err));

        event.preventDefault();
    };

    return (
        <div className={classes.root}>
          <CssBaseline />
          <Container maxWidth="lg" className={classes.container}>
              <div>
                  <Typography variant="h4">
                      Manage versions
                  </Typography>
                  <Grid container>
                      <Grid item xs={6}>
                          <Paper className={classes.paper} elevation={3}>
                              <Typography variant="h5">
                                  Create
                              </Typography>
                              <TextField id="ref" label="Ref" variant="outlined" onChange={e => setRef(e.target.value)}/>
                              <Button className={classes.button} variant="contained" color="primary" onClick={handleSubmit}>Submit</Button>
                          </Paper>
                      </Grid>
                      <Grid item xs={6}>
                          <Paper className={classes.paper} elevation={3}>
                              <Typography variant="h5">
                                  Copy from existing
                              </Typography>
                              <Select
                                  native
                                  value={selectedVersionFirst}
                                  variant="outlined"
                                  onChange={(event) => handleChangeVersionFirst(event)}
                              >
                                  {versions.map((value, index) => {
                                      return <option key={index} value={value}>{value}</option>
                                  })}
                              </Select>
                              <TextField id="ref" label="Ref" variant="outlined" onChange={e => setRef(e.target.value)}/>
                              <Button className={classes.button} variant="contained" color="primary" onClick={handleSubmitCopy}>Submit</Button>
                          </Paper>
                      </Grid>
                      <Grid item xs={6}>
                          <Paper className={classes.paper} elevation={3}>
                              <Typography variant="h5">
                                  Delete
                              </Typography>
                              <Select
                                  native
                                  value={selectedVersionFirst}
                                  variant="outlined"
                                  onChange={(event) => handleChangeVersionFirst(event)}
                              >
                                  {versions.map((value, index) => {
                                      return <option key={index} value={value}>{value}</option>
                                  })}
                              </Select>
                              <Button className={classes.button} variant="contained" color="primary" onClick={handleSubmitDelete}>Submit</Button>
                          </Paper>
                      </Grid>
                      <Grid item xs={6}>
                          <Paper className={classes.paper} elevation={3}>
                              <Typography variant="h5">
                                  Load from file
                              </Typography>
                              <Select
                                  native
                                  value={selectedVersionFile}
                                  variant="outlined"
                                  onChange={(event) => handleChangeVersionFile(event)}
                              >
                                  {versionFiles.map((value, index) => {
                                      return <option key={index} value={value}>{value}</option>
                                  })}
                              </Select>
                              <Button className={classes.button} variant="contained" color="primary" onClick={handleSubmitLoad}>Submit</Button>
                          </Paper>
                      </Grid>
                  </Grid>
              </div>
          </Container>
        </div>
    );
};

export default withStyles(useStyles)(ManageVersion);