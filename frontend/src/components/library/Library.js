import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import axios from 'axios';
import ReactHtmlParser from 'react-html-parser';
import { Link } from "react-router-dom";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import { easyToast, failedToast } from "../utils/toastFunctions";
import Paper from '@material-ui/core/Paper';
import Box from '@material-ui/core/Box';
import Divider from '@material-ui/core/Divider';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardActionArea from '@material-ui/core/CardActionArea';
import {
    Assessment as AssessmentIcon,
    Edit as EditIcon,
    Save as SaveIcon,
    Close as CloseIcon,
    Storage as StorageIcon,
    ImportExport as ImportIcon,
    GetApp as ExportIcon,
    Security as SecurityIcon,
    Category as CategoryIcon,
    Link as LinkIcon,
    Settings as SettingsIcon,
    ShowChart as GraphIcon,
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
        background: 'linear-gradient(135deg,rgb(155, 118, 255) 0%,rgb(75, 103, 162) 100%)',
        color: 'white',
        padding: theme.spacing(2, 3),
        borderRadius: theme.spacing(1),
        marginBottom: theme.spacing(2),
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
    },
    libraryTitle: {
        fontSize: '1.8rem',
        fontWeight: 600,
        marginBottom: theme.spacing(0.5)
    },
    section: {
        marginBottom: theme.spacing(3),
        flex: 1,
        marginRight: theme.spacing(2),
        '&:last-child': {
            marginRight: 0
        }
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
    metricsGrid: {
        marginBottom: theme.spacing(1)
    },
    metricCard: {
        height: '100%',
        transition: 'all 0.2s ease-in-out',
        border: '1px solid #e0e0e0',
        background: '#ffffff',
        '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            borderColor: '#667eea'
        }
    },
    metricContent: {
        padding: theme.spacing(1.5),
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
    },
    metricValue: {
        fontWeight: 600,
        color: '#2c3e50',
        marginBottom: theme.spacing(0.25),
        fontSize: '1.5rem'
    },
    metricLabel: {
        color: '#6c757d',
        fontWeight: 400,
        textTransform: 'uppercase',
        letterSpacing: '0.3px',
        fontSize: '0.7rem'
    },
    operationsGrid: {
        marginBottom: theme.spacing(1)
    },
    operationCard: {
        height: '100%',
        cursor: 'pointer',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
            transform: 'translateY(-1px)',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
        }
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
    editButton: {
        marginTop: theme.spacing(1),
        marginBottom: theme.spacing(2)
    },
    form: {
        backgroundColor: 'white',
        padding: theme.spacing(2),
        borderRadius: theme.spacing(1),
        marginBottom: theme.spacing(2),
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
    },
    formGrid: {
        marginBottom: theme.spacing(1)
    },
    divider: {
        margin: theme.spacing(1.5, 0)
    },
    headerSubtitle: {
        opacity: 0.9,
        marginBottom: theme.spacing(1)
    },
    headerDescription: {
        opacity: 0.8
    },
    formTitle: {
        marginBottom: theme.spacing(2),
        color: '#2c3e50'
    },
    formIcon: {
        marginRight: theme.spacing(0.5),
        verticalAlign: 'middle'
    },
    saveButton: {
        marginTop: theme.spacing(1)
    }
}));

const Library = (props) => {
    const classes = useStyles();
    const { match } = props;

    const version = match.params.id;
    const library = match.params.lib;
    const [libraryReport, setLibraryReport] = useState([]);
    const [edit, setEdit] = useState(false);

    useEffect(() => {
        axios.get('/api/version/' + version + "/" + library + "/report")
            .then(res => {
                setLibraryReport(res.data);
            })
            .catch(err => failedToast(err));
    }, [version, library]);

    const exportToXML = () => {
        axios.get('/api/version/' + version + "/" + library + "/export/xml")
            .then(res => {
                easyToast(res, "Library exported to XML successfully (/output/" + version + "/" + library + ")", "Export failed")
            })
            .catch(err => failedToast("Export failed: " + err));
    };

    const exportToXLSX = () => {
        axios.get('/api/version/' + version + "/" + library + "/export/xlsx")
            .then(res => {
                easyToast(res, "Library exported to XLSX successfully (/output/" + version + "/" + library + ")", "Export failed")
            })
            .catch(err => failedToast("Export failed: " + err));
    };

    const editLibrary = () => {
        setEdit(!edit);
    };

    const updateLibrary = (event) => {
        let data = {
            ref: event.target.library_ref.value,
            name: event.target.library_name.value,
            desc: event.target.library_desc.value,
            revision: event.target.revision.value,
            filename: event.target.library_filename.value,
            enabled: event.target.enabled.value
        };

        axios.put('/api/version/' + version + "/" + library, data)
            .then(res => {
                setLibraryReport(res.data);
                setEdit(false);
                easyToast(res, "Library updated successfully", "Update failed")
            })
            .catch(err => failedToast("Update failed: " + err));

        event.preventDefault();
    };

    return (
        <div className={classes.root}>
            <CssBaseline />
            <Container maxWidth="xl" className={classes.container}>
                {/* Header Section */}
                <Paper className={classes.header} elevation={3}>
                    <Typography variant="h4" className={classes.libraryTitle}>
                        {libraryReport.library_name} ({libraryReport.library_ref})
                    </Typography>
                    <Typography variant="subtitle1" className={classes.headerSubtitle}>
                        Revision {libraryReport.revision}
                    </Typography>
                    <Typography variant="body1" className={classes.headerDescription}>
                        {ReactHtmlParser(libraryReport.library_desc)}
                    </Typography>
                    <Button
                        variant="contained"
                        color="secondary"
                        onClick={editLibrary}
                        className={classes.editButton}
                        startIcon={edit ? <CloseIcon /> : <EditIcon />}
                    >
                        {edit ? "Close" : "Edit Library"}
                    </Button>
                </Paper>

                {/* Edit Form Section */}
                {edit && (
                    <div className={classes.section}>
                        <Paper className={classes.form} elevation={2}>
                            <Typography variant="h6" className={classes.formTitle}>
                                <EditIcon className={classes.formIcon} />
                                Edit Library Details
                            </Typography>
                            <form onSubmit={updateLibrary} noValidate>
                                <Grid container spacing={2} className={classes.formGrid}>
                                    <Grid item xs={12} md={6}>
                                        <TextField
                                            variant="outlined"
                                            fullWidth
                                            id="library_ref"
                                            name="library_ref"
                                            label="Library Reference"
                                            disabled
                                            defaultValue={libraryReport.library_ref}
                                            size="small"
                                        />
                                    </Grid>
                                    <Grid item xs={12} md={6}>
                                        <TextField
                                            variant="outlined"
                                            fullWidth
                                            defaultValue={libraryReport.library_name}
                                            label="Library Name"
                                            id="library_name"
                                            name="library_name"
                                            size="small"
                                        />
                                    </Grid>
                                    <Grid item xs={12}>
                                        <TextField
                                            variant="outlined"
                                            fullWidth
                                            multiline
                                            rows={3}
                                            defaultValue={libraryReport.library_desc}
                                            label="Description"
                                            id="library_desc"
                                            name="library_desc"
                                            size="small"
                                        />
                                    </Grid>
                                    <Grid item xs={12} md={6}>
                                        <TextField
                                            variant="outlined"
                                            fullWidth
                                            defaultValue={libraryReport.revision}
                                            label="Revision"
                                            id="revision"
                                            size="small"
                                        />
                                    </Grid>
                                    <Grid item xs={12} md={6}>
                                        <TextField
                                            variant="outlined"
                                            fullWidth
                                            defaultValue={libraryReport.library_filename}
                                            label="Filename"
                                            id="library_filename"
                                            name="library_filename"
                                            size="small"
                                        />
                                    </Grid>
                                    <Grid item xs={12} md={6}>
                                        <TextField
                                            variant="outlined"
                                            fullWidth
                                            defaultValue={libraryReport.enabled}
                                            label="Enabled"
                                            id="enabled"
                                            size="small"
                                        />
                                    </Grid>
                                    <Grid item xs={12}>
                                        <Button
                                            type="submit"
                                            variant="contained"
                                            color="primary"
                                            startIcon={<SaveIcon />}
                                            className={classes.saveButton}
                                        >
                                            Save Changes
                                        </Button>
                                    </Grid>
                                </Grid>
                            </form>
                        </Paper>
                    </div>
                )}

                <Divider className={classes.divider} />

                {/* Metrics Section */}
                <div className={classes.section}>
                    <Typography variant="h4" className={classes.sectionTitle}>
                        <AssessmentIcon /> Library Statistics
                    </Typography>
                    <Grid container spacing={2} className={classes.metricsGrid}>
                        <Grid item xs={4} sm={3} md={2} lg={1}>
                            <Card className={classes.metricCard}>
                                <CardContent className={classes.metricContent}>
                                    <Box display="flex" flexDirection="column" alignItems="center" textAlign="center">
                                        <Typography variant="h4" className={classes.metricValue}>
                                            {libraryReport.revision}
                                        </Typography>
                                        <Typography variant="caption" className={classes.metricLabel}>
                                            Revision
                                        </Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={4} sm={3} md={2} lg={1}>
                            <Card className={classes.metricCard}>
                                <CardContent className={classes.metricContent}>
                                    <Box display="flex" flexDirection="column" alignItems="center" textAlign="center">
                                        <Typography variant="h4" className={classes.metricValue}>
                                            {libraryReport.num_risk_patterns}
                                        </Typography>
                                        <Typography variant="caption" className={classes.metricLabel}>
                                            Risk Patterns
                                        </Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={4} sm={3} md={2} lg={1}>
                            <Card className={classes.metricCard}>
                                <CardContent className={classes.metricContent}>
                                    <Box display="flex" flexDirection="column" alignItems="center" textAlign="center">
                                        <Typography variant="h4" className={classes.metricValue}>
                                            {libraryReport.num_usecases}
                                        </Typography>
                                        <Typography variant="caption" className={classes.metricLabel}>
                                            Use Cases
                                        </Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={4} sm={3} md={2} lg={1}>
                            <Card className={classes.metricCard}>
                                <CardContent className={classes.metricContent}>
                                    <Box display="flex" flexDirection="column" alignItems="center" textAlign="center">
                                        <Typography variant="h4" className={classes.metricValue}>
                                            {libraryReport.num_threats}
                                        </Typography>
                                        <Typography variant="caption" className={classes.metricLabel}>
                                            Threats
                                        </Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={4} sm={3} md={2} lg={1}>
                            <Card className={classes.metricCard}>
                                <CardContent className={classes.metricContent}>
                                    <Box display="flex" flexDirection="column" alignItems="center" textAlign="center">
                                        <Typography variant="h4" className={classes.metricValue}>
                                            {libraryReport.num_rules}
                                        </Typography>
                                        <Typography variant="caption" className={classes.metricLabel}>
                                            Rules
                                        </Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={4} sm={3} md={2} lg={1}>
                            <Card className={classes.metricCard}>
                                <CardContent className={classes.metricContent}>
                                    <Box display="flex" flexDirection="column" alignItems="center" textAlign="center">
                                        <Typography variant="h4" className={classes.metricValue}>
                                            {libraryReport.num_component_definitions}
                                        </Typography>
                                        <Typography variant="caption" className={classes.metricLabel}>
                                            Component Definitions
                                        </Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </div>

                <Divider className={classes.divider} />

                <div style={{ display: "flex", flexDirection: "row", gap: "16px" }}>
                    {/* Content Management Operations */}
                    <div className={classes.section}>
                        <Typography variant="h4" className={classes.sectionTitle}>
                            <StorageIcon /> Content Management
                        </Typography>
                        <Grid container spacing={2} className={classes.operationsGrid}>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/" + library + "/manageRiskPatterns"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <SecurityIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Manage Risk Patterns
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/" + library + "/manageComponents"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <CategoryIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Manage Component Definitions
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/" + library + "/manageRelations"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <LinkIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Manage Relations
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                        </Grid>
                    </div>

                    {/* Analysis & Export Operations */}
                    <div className={classes.section}>
                        <Typography variant="h4" className={classes.sectionTitle}>
                            <ImportIcon /> Analysis & Export
                        </Typography>
                        <Grid container spacing={2} className={classes.operationsGrid}>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/" + library + "/rulesGraph"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <GraphIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Show Rules Graph
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea onClick={exportToXML}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <ExportIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Export to XML
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea onClick={exportToXLSX}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <ExportIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Export to XLSX
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/" + library + "/setMitigationValues"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <SettingsIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Balance Mitigation Values
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                        </Grid>
                    </div>
                </div>
            </Container>
        </div>
    );
};

export default Library;