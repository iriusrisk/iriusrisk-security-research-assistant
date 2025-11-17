import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import axios from 'axios';
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import { easyToast, failedToast } from "../utils/toastFunctions";
import { ForceGraph2D } from "react-force-graph";
import { Link } from "react-router-dom";
import Paper from '@material-ui/core/Paper';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardActionArea from '@material-ui/core/CardActionArea';
import {
    Save as SaveIcon,
    FolderOpen as LoadIcon,
    DeleteSweep as CleanIcon,
    Assessment as AssessmentIcon,
    CompareArrows as CompareIcon,
    CallMerge as MergeIcon,
    Settings as SettingsIcon,
    Storage as StorageIcon
} from '@material-ui/icons';

const useStyles = makeStyles((theme) => ({
    root: {
        display: 'flex',
        paddingRight: '16px',
        backgroundColor: '#f5f5f5',
        minHeight: '100vh'
    },
    container: {
        paddingTop: theme.spacing(2),
        paddingBottom: theme.spacing(2),
    },
    header: {
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: theme.spacing(2, 3),
        borderRadius: theme.spacing(1),
        marginBottom: theme.spacing(2),
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
    },
    projectTitle: {
        fontSize: '1.8rem',
        fontWeight: 600,
        marginBottom: theme.spacing(0.5)
    },
    section: {
        marginBottom: theme.spacing(3)
    },
    sectionTitle: {
        fontSize: '1.4rem',
        fontWeight: 500,
        marginBottom: theme.spacing(1.5),
        color: '#2c3e50',
        display: 'flex',
        alignItems: 'center',
        '& svg': {
            marginRight: theme.spacing(0.5),
            color: '#667eea'
        }
    },
    operationsGrid: {
        marginBottom: theme.spacing(1)
    },
    groupedOperationCard: {
        height: '100%',
        cursor: 'pointer',
        transition: 'all 0.2s ease-in-out',
        border: '1px solid #e0e0e0',
        '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 6px 20px rgba(0,0,0,0.12)',
            borderColor: '#667eea'
        }
    },
    groupedOperationContent: {
        padding: theme.spacing(1.5),
        textAlign: 'center',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center'
    },
    operationIcon: {
        fontSize: 32,
        marginBottom: theme.spacing(1),
        color: '#667eea'
    },
    operationTitle: {
        fontSize: '0.9rem',
        fontWeight: 500,
        color: '#2c3e50',
        textAlign: 'center',
        lineHeight: 1.2
    },
    divider: {
        margin: theme.spacing(1.5, 0)
    }
}));

const Marketplace = (props) => {
    const classes = useStyles();
    const { project } = props;

    return (
        <div className={classes.root}>
            <CssBaseline />
            <Container maxWidth="xl" className={classes.container}>
                {/* Header Section */}
                <Paper className={classes.header} elevation={3}>
                    <Typography variant="h4" className={classes.projectTitle}>
                        {project}
                    </Typography>
                    <Typography variant="subtitle1" style={{ opacity: 0.9 }}>
                        Marketplace Management Dashboard
                    </Typography>
                </Paper>

                {/* Project Management Operations */}
                <div className={classes.section}>
                    <Typography variant="h4" className={classes.sectionTitle}>
                        <StorageIcon /> Marketplace Management
                    </Typography>
                    <Grid container spacing={2} className={classes.operationsGrid}>
                        {project !== "" && (
                            <Grid item xs={6} sm={4} md={3} lg={2}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/marketplace/manageReleaseNotes"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <SaveIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Manage Release Notes
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                        )}
                    </Grid>
                </div>
            </Container>
        </div>
    );
};

export default Marketplace;