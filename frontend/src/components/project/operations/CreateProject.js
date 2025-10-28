import React, { useState } from 'react';
import { withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import { failedToast, successToast } from "../../utils/toastFunctions";
import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
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

const CreateProject = (props) => {
    const { classes, handleProjectChange } = props;
    const [ref, setRef] = useState("");

    const handleSubmit = (event) => {
        let project = {
            "ref": ref,
            "name": "",
            "desc": ""
        };
        axios.post('/api/project', project)
            .then(res => {
                if(res.status === 200){
                    let versions = Object.keys(res.data.versions);
                    handleProjectChange(res.data.ref, versions);
                    successToast("Project created successfully");
                }else{
                    failedToast("Creating project failed");
                }
            })
            .catch(err => failedToast("Creating project failed: " + err));

        event.preventDefault();
    };

    return (
        <div className={classes.root}>
          <CssBaseline />
          <Container maxWidth="lg" className={classes.container}>
              <div>
                  <Typography variant="h4">
                    Create new project
                  </Typography>
                  <Paper className={classes.paper} elevation={3}>
                      <TextField id="ref" label="Project name" variant="outlined" onChange={e => setRef(e.target.value)}/>
                      <Button className={classes.button} variant="contained" color="primary" onClick={handleSubmit}>Submit</Button>
                  </Paper>
              </div>
          </Container>
        </div>
    );
};

export default withStyles(useStyles)(CreateProject);