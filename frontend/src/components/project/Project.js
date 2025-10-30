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

const Project = (props) => {
    const classes = useStyles();
    const { project } = props;
    const [data] = useState({ "nodes": [], "links": [] });
    const [graph] = useState(false);

    useEffect(() => {
        // Component did mount logic can go here
    }, []);

    const saveProject = () => {
        axios.get('/api/project/save')
            .then(res => {
                easyToast(res, "Project saved successfully", "Saving project failed");
            })
            .catch(err => failedToast("Saving project failed: " + err));
    };

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
                        Project Management Dashboard
                    </Typography>
                </Paper>

                {/* Project Management Operations */}
                <div className={classes.section}>
                    <Typography variant="h4" className={classes.sectionTitle}>
                        <StorageIcon /> Project Management
                    </Typography>
                    <Grid container spacing={2} className={classes.operationsGrid}>
                        {project !== "" && (
                            <Grid item xs={6} sm={4} md={3} lg={2}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea onClick={saveProject}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <SaveIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Save Project
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                        )}
                        <Grid item xs={6} sm={4} md={3} lg={2}>
                            <Card className={classes.groupedOperationCard}>
                                <CardActionArea component={Link} to={"/project/loadProject"}>
                                    <CardContent className={classes.groupedOperationContent}>
                                        <LoadIcon className={classes.operationIcon} />
                                        <Typography className={classes.operationTitle}>
                                            Load Project
                                        </Typography>
                                    </CardContent>
                                </CardActionArea>
                            </Card>
                        </Grid>
                        {project !== "" && (
                            <Grid item xs={6} sm={4} md={3} lg={2}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/project/manageVersion"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <SettingsIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Manage Versions
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                        )}
                    </Grid>
                </div>

                {/* Analysis & Maintenance Operations */}
                {project !== "" && (
                    <div className={classes.section}>
                        <Typography variant="h4" className={classes.sectionTitle}>
                            <AssessmentIcon /> Analysis & Maintenance
                        </Typography>
                        <Grid container spacing={2} className={classes.operationsGrid}>
                            <Grid item xs={6} sm={4} md={3} lg={2}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/project/cleanFolders"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <CleanIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Clean Folders
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={6} sm={4} md={3} lg={2}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/project/createChangelogBetweenVersions"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <CompareIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Changelog Between Versions
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={6} sm={4} md={3} lg={2}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/project/createChangelogBetweenLibraries"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <CompareIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Changelog Between Libraries
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={6} sm={4} md={3} lg={2}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/project/mergeLibraries"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <MergeIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Merge Libraries
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                        </Grid>
                    </div>
                )}
                { graph &&

                <ForceGraph2D graphData={data}
                              backgroundColor={"#e5e5e5"}
                              width={1000}
                              height={500}
                              enablePointerInteraction={true}
                              enableNodeDrag={true}
                              nodeLabel="name"
                              linkDirectionalArrowLength={10}
                              linkDirectionalArrowRelPos={1}
                              linkWidth={3}
                              nodeId="id"
                              nodeVal={10}
                              nodeCanvasObject={(node, ctx) => {
                                  const label = node.name;

                                  ctx.beginPath();
                                  ctx.lineWidth = 1;
                                  ctx.strokeStyle = node.color;
                                  ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
                                  ctx.fillStyle = node.color;
                                  ctx.fill();
                                  ctx.stroke();
                                  ctx.closePath();

                                  ctx.beginPath();
                                  ctx.fillStyle = "#000000";
                                  ctx.fillText(label, node.x + 9, node.y + 2);
                                  ctx.closePath();
                              }}
                />
                }
            </Container>
        </div>
    );
};

export default Project;