import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import AccordionSummary from "@material-ui/core/AccordionSummary";
import AccordionDetails from "@material-ui/core/AccordionDetails";
import Grid from "@material-ui/core/Grid";
import Accordion from "@material-ui/core/Accordion";
import Button from "@material-ui/core/Button";
import { easyToast, failedToast } from "../../utils/toastFunctions";

const useStyles = makeStyles((theme) => ({
    root: {
        display: 'flex',
    },
    container: {
        paddingTop: theme.spacing(4),
        paddingBottom: theme.spacing(4),
    },
}));

const SetMitigationValues = (props) => {
    const classes = useStyles();
    const { match } = props;
    
    const [version, setVersion] = useState(match.params.id);
    const [library, setLibrary] = useState(match.params.lib);
    const [data, setData] = useState({"risk_patterns": []});
    const [accordion1, setAccordion1] = useState(false);
    const [accordion2, setAccordion2] = useState(false);

    useEffect(() => {
        axios.get('/api/version/' + version + '/' + library + '/checkMitigation')
            .then(res => {
                setAccordion1(true);
                setData(res.data);
            })
            .catch(err => failedToast(err));
    }, [version, library]);

    const handleAccordion1 = () => {
        setAccordion1(!accordion1);
    };

    const balanceMitigation = () => {
        axios.get('/api/version/' + version + '/' + library + '/balanceMitigation')
            .then(res => {
                easyToast(res, "Mitigation values balanced", "Mitigation balance failed");
                setData(res.data);
            })
            .catch(err => failedToast(err));
    };

    return (
        <div className={classes.root}>
            <CssBaseline/>
            <Container maxWidth="lg" className={classes.container}>
                <div>
                    <Typography variant="h4">
                        Set mitigation values
                    </Typography>
                    {data.risk_patterns.length === 0 &&
                     <Typography variant="h6">
                         Mitigation values are correct
                     </Typography>
                    }
                    {data.risk_patterns.length !== 0 &&
                    <Accordion expanded={accordion1} onChange={handleAccordion1}>
                        <AccordionSummary
                            aria-controls="panel1a-content"
                            id="panel1a-header"
                        >
                            <Typography variant="h6">Wrong mitigation values ({data.risk_patterns.length})</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                             <div>
                                 <Button
                                     variant="contained"
                                     color="primary"
                                     onClick={balanceMitigation}
                                 >
                                     Balance mitigation values automatically
                                 </Button>
                             <Grid container spacing={3}>
                                 {data.risk_patterns.map((value, index) => {
                                     return <Grid key={index} item>
                                         <Typography variant="h6">Risk pattern: {value.ref}</Typography>
                                         <Grid container>
                                             {value.threats.map((value2, index2) => {
                                                 return [
                                                     <Grid item xs={12}>
                                                         Use case: {value2.usecaseRef} | Threat: {value2.threatRef}
                                                     </Grid>,
                                                     <Grid item xs={12}>
                                                         {value2.message}
                                                     </Grid>,
                                                     <Grid item xs={4}>
                                                         Total mitigation: {value2.total}
                                                     </Grid>,
                                                     <Grid container>
                                                         <Grid item xs={12}>
                                                             Relations:
                                                         </Grid>
                                                         {value2.relations.map((value3) => {
                                                             return [
                                                                 // <Grid item xs={4}>
                                                                 //     Weakness: {value3.weaknessRef}
                                                                 // </Grid>,
                                                                 <Grid item xs={6}>
                                                                     Control: {value3.controlRef}
                                                                 </Grid>,
                                                                 <Grid item xs={6}>
                                                                     Mitigation: {value3.mitigation}
                                                                 </Grid>,
                                                             ]
                                                         })}
                                                     </Grid>,
                                                 ]
                                             })}
                                         </Grid>
                                     </Grid>
                                 })}
                             </Grid>
                             </div>
                        </AccordionDetails>
                    </Accordion>
                    }
                </div>
            </Container>
        </div>
    );
};

export default SetMitigationValues;