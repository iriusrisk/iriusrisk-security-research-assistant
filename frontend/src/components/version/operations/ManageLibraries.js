import React, { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import { failedToast, successToast } from "../../utils/toastFunctions";
import TextField from "@material-ui/core/TextField";
import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import Grid from "@material-ui/core/Grid";

const useStyles = makeStyles((theme) => ({
    root: {
      display: 'flex',
    },
    container: {
      paddingTop: theme.spacing(4),
      paddingBottom: theme.spacing(4),
    },
    paper: {
        padding: "20px",
        margin: "5px"
    },
    button: {
        float: "right"
    }
}));

const ManageLibraries = ({ version }) => {
    const classes = useStyles();
    const [ref, setRef] = useState("");
    const [libraries, setLibraries] = useState([]);

    const createLibrary = () => {
        let postData = {
            "libraryRef": ref
        };
        axios.post("/api/version/" + version + "/library", postData)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Update the libraries list with the returned library object
                    const newLibraries = [...libraries, res.data];
                    setLibraries(newLibraries);
                    setRef(""); // Clear the input field
                    successToast("Library created");
                } else {
                    failedToast("Library couldn't be created");
                }
            })
            .catch(err => failedToast(err));
    };

    const handleSubmit = (event) => {
        createLibrary();
        event.preventDefault();
    };

    return (
        <div className={classes.root}>
            <CssBaseline />
            <Container maxWidth="lg" className={classes.container}>
                <div>
                    <Typography variant="h4">
                        Manage libraries
                    </Typography>
                    <Grid container>
                        <Grid item xs={6}>
                            <Paper className={classes.paper} elevation={3}>
                                <Typography variant="h5">
                                    Create
                                </Typography>
                                <TextField 
                                    id="ref" 
                                    label="New library ref" 
                                    variant="outlined" 
                                    value={ref}
                                    onChange={e => setRef(e.target.value)}
                                />
                                <Button 
                                    className={classes.button} 
                                    variant="contained" 
                                    color="primary" 
                                    onClick={handleSubmit}
                                >
                                    Submit
                                </Button>
                            </Paper>
                        </Grid>
                    </Grid>
                </div>
            </Container>
        </div>
    );
};

export default ManageLibraries;