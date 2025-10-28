import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import Button from "@material-ui/core/Button";
import Grid from "@material-ui/core/Grid";
import { failedToast } from "../../../utils/toastFunctions";

const useStyles = makeStyles((theme) => ({
    root: {
      display: 'flex',
    },
    container: {
      paddingTop: theme.spacing(4),
      paddingBottom: theme.spacing(4),
    },
}));

const StatisticsReport = (props) => {
    const classes = useStyles();
    const { version, libraries, back } = props;
    
    const [items, setItems] = useState([]);

    useEffect(() => {
        axios.get('/version/' + version)
            .then(res => {
                let fullVersion = res.data;
                let its = [];

                for (const [libKey, libValue] of Object.entries(fullVersion.libraries)) {
                    if (libraries.includes(libKey)) {
                        for (const [rpKey, rpValue] of Object.entries(libValue.riskPatterns)) {
                            let uc = new Set();
                            let t = new Set();
                            let w = new Set();
                            let c = new Set();

                            // Filter relations by risk pattern before counting elements
                            const filteredRelations = Object.values(libValue.relations).filter(v => v.riskPatternUuid === rpKey);
                            filteredRelations.forEach(v => {
                                uc.add(v.usecaseUuid);
                                t.add(v.threatUuid);
                                w.add(v.weaknessUuid);
                                c.add(v.controlUuid);
                            });

                            t.delete("");
                            w.delete("");
                            c.delete("");

                            its.push({
                                rp: rpValue.ref,
                                numUc: uc.size,
                                numT: t.size,
                                numW: w.size,
                                numC: c.size
                            })
                        }
                    }
                }

                setItems(its);
            })
            .catch(err => failedToast(err));
    }, [version, libraries]);

    return (
        <div className={classes.root}>
            <CssBaseline />
            <Container maxWidth="lg" className={classes.container}>
                <Typography variant="h4">
                    Statistics Report
                </Typography>
                <div>
                    <Button variant="contained" color="primary" onClick={back}>Back</Button>
                    <div>Version: {version}</div>
                    <div>
                        <Grid container>
                            <Grid item xs={4}>
                                Risk pattern
                            </Grid>
                            <Grid item xs={2}>
                                Use cases
                            </Grid>
                            <Grid item xs={2}>
                                Threats
                            </Grid>
                            <Grid item xs={2}>
                                Weaknesses
                            </Grid>
                            <Grid item xs={2}>
                                Controls
                            </Grid>
                            {items.map((value, index) => {
                                return [
                                    <Grid item xs={4} key={"rp" + index}>{value.rp}</Grid>,
                                    <Grid item xs={2} key={"uc" + index}>{value.numUc}</Grid>,
                                    <Grid item xs={2} key={"t" + index}>{value.numT}</Grid>,
                                    <Grid item xs={2} key={"w" + index}>{value.numW}</Grid>,
                                    <Grid item xs={2} key={"c" + index}>{value.numC}</Grid>
                                ]
                            })}
                        </Grid>
                    </div>
                </div>
            </Container>
        </div>
    );
};

export default StatisticsReport;