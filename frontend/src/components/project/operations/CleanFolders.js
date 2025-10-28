import React, { useState } from 'react';
import { withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import { failedToast, successToast } from "../../utils/toastFunctions";
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

const CleanFolders = (props) => {
    const { classes } = props;
    const [selectedProject, setSelectedProject] = useState("output");
    const [projects] = useState(["output","versions","projects"]);

    const handleChange = (event) => {
        setSelectedProject(event.target.value);
    };

    const handleSubmit = (event) => {
        axios.get('/api/project/cleanFolder/' + selectedProject)
            .then(() => {
                successToast("Folder cleaned successfully");
            })
            .catch(err => failedToast("Cleaning folder failed: " + err));

        event.preventDefault();
    };

    return (
        <div className={classes.root}>
          <CssBaseline />
          <Container maxWidth="lg" className={classes.container}>
              <div>
                  <Typography variant="h4">
                    Clean folders
                  </Typography>
                  <Typography variant="body1">
                      This operation will remove ALL files on the selected folder, be careful!
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

export default withStyles(useStyles)(CleanFolders);