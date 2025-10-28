import React, { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import { failedToast, successToast } from "../../utils/toastFunctions";
import Button from "@material-ui/core/Button";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";

const useStyles = makeStyles((theme) => ({
    root: {
      display: 'flex',
    },
    container: {
      paddingTop: theme.spacing(4),
      paddingBottom: theme.spacing(4),
    },
}));

const CleanVersion = (props) => {
    const classes = useStyles();
    const { version } = props;
    
    const [removed, setRemoved] = useState([]);

    const cleanVersion = () => {
        axios.get('/version/' + version + '/clean')
            .then(res => {
                if (res.status === 200) {
                    successToast("Version cleaned successfully");
                    setRemoved(res.data);
                }
            })
            .catch(err => failedToast("Cleaning version failed: " + err));
    };

    return (
        <div className={classes.root}>
            <CssBaseline />
            <Container maxWidth="lg" className={classes.container}>
                <div>
                    <Typography variant="h4">
                        Clean version
                    </Typography>
                    <Typography variant="body1">
                        This function will remove unused content
                    </Typography>
                    <Button variant="contained" color="primary" onClick={cleanVersion}>Clean version {version}</Button>
                    <List>
                        {removed.map((value, index) => {
                            return <ListItem key={index}>{value}</ListItem>
                        })}
                    </List>
                </div>
            </Container>
        </div>
    );
};

export default CleanVersion;