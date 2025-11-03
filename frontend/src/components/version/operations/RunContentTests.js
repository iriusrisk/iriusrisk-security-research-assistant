import React, {useState, useEffect} from 'react';
import {makeStyles} from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import Grid from "@material-ui/core/Grid";
import List from '@material-ui/core/List';
import ListItem from "@material-ui/core/ListItem";
import SimpleCard from "../../utils/SimpleCard";
import {failedToast} from "../../utils/toastFunctions";

const useStyles = makeStyles((theme) => ({
    root: {
        display: 'flex',
    },
    container: {
        paddingTop: theme.spacing(4),
        paddingBottom: theme.spacing(4),
    },
    rootGreen: {
        backgroundColor: "#b7f9b2",
        "&:hover": {
            backgroundColor: "#13e29d",
        },
        "&:active": {
            backgroundColor: "#16cb48",
        },
    },
    rootRed: {
        backgroundColor: "#f97678",
        "&:hover": {
            backgroundColor: "#ff574d",
        },
        "&:active": {
            backgroundColor: "#d94843",
        },
    },
}));

const RunContentTests = ({version}) => {
    const classes = useStyles();
    const [data, setData] = useState({
        numSuccessTests: 0,
        numFailedTests: 0,
        testResults: {}
    });
    const [showErrors, setShowErrors] = useState('');

    useEffect(() => {
        axios.get('/api/version/' + version + '/test')
            .then(res => {
                setData({
                    numSuccessTests: res.data.num_success_tests ?? res.data.numSuccessTests ?? 0,
                    numFailedTests: res.data.num_failed_tests ?? res.data.numFailedTests ?? 0,
                    testResults: res.data.test_results ?? res.data.testResults ?? {}
                });
            })
            .catch(err => failedToast(err));
    }, [version]);

    const handleChange = (value) => {
        setShowErrors(value);
    };

    return (
        <div className={classes.root}>
            <CssBaseline/>
            <Container maxWidth="lg" className={classes.container}>
                <Typography variant="h4">
                    Run content tests
                </Typography>
                <Grid container>
                    <Grid item xs={6}>
                        <SimpleCard subtitle="Passed tests" title={data.numSuccessTests}/>
                    </Grid>
                    <Grid item xs={6}>
                        <SimpleCard subtitle="Failed tests" title={data.numFailedTests}/>
                    </Grid>
                    <Grid item xs={3}>
                        <List>
                            {data.testResults && Object.keys(data.testResults).sort().map((value, index) => {
                                return <div key={index}>
                                    {data.testResults[value].length === 0 &&
                                     <ListItem className={classes.rootGreen}
                                               onClick={() => handleChange(value)}>{value}</ListItem>
                                    }
                                    {data.testResults[value].length !== 0 &&
                                     <ListItem className={classes.rootRed}
                                               onClick={() => handleChange(value)}>{value}</ListItem>
                                    }
                                </div>

                            })}
                        </List>
                    </Grid>
                    <Grid item xs={9}>
                        {showErrors && data.testResults && data.testResults[showErrors] &&
                         <div>
                             <Typography variant="h6">
                                 {showErrors}
                             </Typography>
                             <List>
                                 {data.testResults[showErrors].map((value, index) => {
                                     return <ListItem key={index} className={classes.rootRed}>{value}</ListItem>
                                 })}
                             </List>
                         </div>

                        }
                    </Grid>
                </Grid>

            </Container>
        </div>
    );
};

export default RunContentTests;