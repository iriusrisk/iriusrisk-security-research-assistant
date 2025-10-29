import React, { useState, useEffect } from 'react';
import { withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import { failedToast, successToast, warnToast } from "../../utils/toastFunctions";
import Select from "@material-ui/core/Select";
import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";

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

const LoadProject = (props) => {
    const { classes, handleProjectChange } = props;
    const [selectedProject, setSelectedProject] = useState("");
    const [projects, setProjects] = useState([]);

    useEffect(() => {
        axios.get('/api/project/list')
            .then(res => {
                if(res.status === 200){
                    if(res.data.length === 0){
                        warnToast("No projects available. Create a new one and save it");
                    }else{
                        setProjects(res.data);
                        setSelectedProject(res.data[0]);
                    }
                }else{
                    failedToast("Failed to retrieve projects");
                }
            })
            .catch(err => failedToast("Failed to retrieve projects: " + err));
    }, []);

    const handleChange = (event) => {
        setSelectedProject(event.target.value);
    };

    const handleSubmit = (event) => {
        axios.get('/api/project/load/' + selectedProject)
            .then(res => {
                let versions = [];
                Object.keys(res.data.versions).forEach(element => versions.push(element));
                handleProjectChange(res.data.ref, versions);
                successToast("Project loaded successfully");
            })
            .catch(err => failedToast("Loading project failed: " + err));

        event.preventDefault();
    };

    return (
        <div className={classes.root}>
          <CssBaseline />
          <Container maxWidth="lg" className={classes.container}>
              <div>
                  <Typography variant="h4">
                    Load project
                  </Typography>
                  <Paper className={classes.paper} elevation={3}>
                      <Select
                          native
                          value={selectedProject}
                          variant="outlined"
                          onChange={handleChange}
                      >
                          {projects.map((value, index) => {
                              return <option key={index} value={value}>{value}</option>
                          })}
                      </Select>
                      <Button className={classes.button} variant="contained" color="primary" onClick={handleSubmit}>Submit</Button>
                  </Paper>
              </div>
          </Container>
        </div>
    );
};

export default withStyles(useStyles)(LoadProject);