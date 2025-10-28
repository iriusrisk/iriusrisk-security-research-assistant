import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import axios from 'axios';
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import SimpleCard from "../utils/SimpleCard";
import { easyToast, failedToast } from "../utils/toastFunctions";
import AddCircleIcon from '@material-ui/icons/AddCircle';
import { Link } from "react-router-dom";
import IconButton from "@material-ui/core/IconButton";
import Paper from '@material-ui/core/Paper';
import Box from '@material-ui/core/Box';
import Divider from '@material-ui/core/Divider';
import Chip from '@material-ui/core/Chip';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardActionArea from '@material-ui/core/CardActionArea';
import {
    Save as SaveIcon,
    Clear as CleanIcon,
    LibraryBooks as LibraryIcon,
    Assignment as UseCaseIcon,
    Security as ThreatIcon,
    BugReport as WeaknessIcon,
    VerifiedUser as ControlIcon,
    Category as CategoryIcon,
    Book as ReferenceIcon,
    Star as StandardIcon,
    Build as BuildIcon,
    Assessment as AssessmentIcon,
    Description as ReportIcon,
    ImportExport as ImportIcon,
    GetApp as ExportIcon,
    Code as CodeIcon,
    Add as AddIcon,
    Settings as SettingsIcon,
    Storage as StorageIcon,
    BugReport as TestIcon,
    NoteAdd as CreateIcon
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
    versionTitle: {
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
    librariesGrid: {
        marginBottom: theme.spacing(1)
    },
    libraryCard: {
        height: '100%',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
            transform: 'translateY(-1px)',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
        }
    },
    addLibraryButton: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        minHeight: '80px',
        border: '2px dashed #ccc',
        borderRadius: theme.spacing(0.5),
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.05)'
        }
    },
    chip: {
        margin: theme.spacing(0.25),
        backgroundColor: '#e3f2fd',
        color: '#1976d2'
    },
    divider: {
        margin: theme.spacing(1.5, 0)
    }
}));

const Version = (props) => {
    const classes = useStyles();
    const { match } = props;
    const versionId = match.params.id;

    const [version, setVersion] = useState(versionId);
    const [versionReport, setVersionReport] = useState([]);
    const [libraryReport, setLibraryReport] = useState([]);

    const fetchVersionData = (versionParam) => {
        axios.get('/version/' + versionParam + "/report")
            .then(res => {
                setVersionReport(res.data);
                setLibraryReport(res.data.libraryReport);
            })
            .catch(err => failedToast(err));
    };

    useEffect(() => {
        fetchVersionData(version);
    }, [version]);

    useEffect(() => {
        if (versionId !== version) {
            setVersion(versionId);
        }
    }, [versionId, version]);

    const exportToXML = () => {
        axios.get('/version/' + version + "/export/xml")
            .then(res => {
                easyToast(res, "Version exported to XML successfully (/output/" + version + ")", "Export failed");
            })
            .catch(err => failedToast("Export failed: " + err));
    };

    const exportToXLSX = () => {
        axios.get('/version/' + version + "/export/xlsx")
            .then(res => {
                easyToast(res, "Version exported to XLSX successfully (/output/" + version + ")", "Export failed");
            })
            .catch(err => failedToast("Export failed: " + err));
    };

    const deleteLibrary = (props) => {
        const parts = props.link.split('/');
        const library = parts[parts.length - 1];
        const versionParam = parts[parts.length - 2];

        let postData = {
            "libraryRef": library
        };
        console.log(postData);

        axios.delete("/version/" + versionParam + "/library", { data: postData })
            .then(res => {
                easyToast(res, "Library deleted successfully", "Deleting library failed");
                if (res.status === 200) {
                    fetchVersionData(match.params.id);
                }
            })
            .catch(err => failedToast("Deleting library failed: " + err));
    };

    const exportLibraryToXML = (props) => {
        const parts = props.link.split('/');
        const library = parts[parts.length - 1];
        const versionParam = parts[parts.length - 2];

        axios.get('/version/' + versionParam + "/" + library + "/export/xml")
            .then(res => {
                easyToast(res, "Library exported to XML successfully (/output/" + versionParam + "/" + library + ")", "Export failed")
            })
            .catch(err => failedToast("Export failed: " + err));
    };

    const fixNonASCIIValues = () => {
        axios.get('/version/' + version + "/fix/ascii")
            .then(res => {
                easyToast(res, "ASCII Values fixed successfully", "ASCII fix failed")
            })
            .catch(err => failedToast("ASCII fix failed: " + err));
    };

    const incrementRevision = (props) => {
        const parts = props.link.split('/');
        const library = parts[parts.length - 1];
        const versionParam = parts[parts.length - 2];

        const postData = {
            "libraryRef": library
        };

        axios.put("/version/" + versionParam + "/library", postData)
            .then(res => {
                easyToast(res, "Library revision incremented successfully", "Incrementing library revision failed");
                if (res.status === 200) {
                    fetchVersionData(match.params.id);
                }
            })
            .catch(err => failedToast("Incrementing library revision failed: " + err));
    };

    const saveVersion = () => {
        axios.get('/version/' + version + '/save')
            .then(res => {
                easyToast(res, "Version saved successfully", "Saving version failed");
            })
            .catch(err => failedToast("Saving version failed: " + err));
    };

    // Sort library report for display
    const sortedLibraryReport = [...libraryReport].sort((a, b) =>
        (a.libraryRef.toLowerCase() > b.libraryRef.toLowerCase()) ? 1 :
            ((b.libraryRef.toLowerCase() > a.libraryRef.toLowerCase()) ? -1 : 0)
    );

    return (
        <div className={classes.root}>
            <CssBaseline />
            <Container maxWidth="xl" className={classes.container}>
                {/* Header Section */}
                <Paper className={classes.header} elevation={3}>
                    <Typography variant="h4" className={classes.versionTitle}>
                        Version {versionReport.version}
                    </Typography>
                    <Typography variant="subtitle1" style={{ opacity: 0.9 }}>
                        Library Management Dashboard
                    </Typography>
                </Paper>

                {/* Metrics Section */}
                <div className={classes.section}>
                    <Typography variant="h4" className={classes.sectionTitle}>
                        <AssessmentIcon /> Version Statistics
                    </Typography>
                    <Grid container spacing={2} className={classes.metricsGrid}>
                        <Grid item xs={4} sm={3} md={2} lg={1}>
                            <Card className={classes.metricCard}>
                                <CardContent className={classes.metricContent}>
                                    <Box display="flex" flexDirection="column" alignItems="center" textAlign="center">
                                        <Typography variant="h4" className={classes.metricValue}>
                                            {versionReport.numLibraries}
                                        </Typography>
                                        <Typography variant="caption" className={classes.metricLabel}>
                                            Libraries
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
                                            {versionReport.numRiskPatterns}
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
                                            {versionReport.numUsecases}
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
                                            {versionReport.numThreats}
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
                                            {versionReport.numWeaknesses}
                                        </Typography>
                                        <Typography variant="caption" className={classes.metricLabel}>
                                            Weaknesses
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
                                            {versionReport.numControls}
                                        </Typography>
                                        <Typography variant="caption" className={classes.metricLabel}>
                                            Controls
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
                                            {versionReport.numCategories}
                                        </Typography>
                                        <Typography variant="caption" className={classes.metricLabel}>
                                            Categories
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
                                            {versionReport.numReferences}
                                        </Typography>
                                        <Typography variant="caption" className={classes.metricLabel}>
                                            References
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
                                            {versionReport.numStandards}
                                        </Typography>
                                        <Typography variant="caption" className={classes.metricLabel}>
                                            Standards
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
                                            {versionReport.numComponents}
                                        </Typography>
                                        <Typography variant="caption" className={classes.metricLabel}>
                                            Components
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
                                            {versionReport.numRules}
                                        </Typography>
                                        <Typography variant="caption" className={classes.metricLabel}>
                                            Rules
                                        </Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </div>

                <Divider className={classes.divider} />

                <div style={{ display: "flex", flexDirection: "row", gap: "16px" }}>
                    {/* Version Management Operations */}
                    <div className={classes.section}>
                        <Typography variant="h4" className={classes.sectionTitle}>
                            <SettingsIcon /> Version Management
                        </Typography>
                        <Grid container spacing={2} className={classes.operationsGrid}>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea onClick={saveVersion}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <SaveIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Save Version
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/cleanVersion"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <CleanIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Clean Version
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/createElements"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <CreateIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Create Elements
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                        </Grid>
                    </div>
                    {/* Import/Export Operations */}
                    <div className={classes.section}>
                        <Typography variant="h4" className={classes.sectionTitle}>
                            <ImportIcon /> Import/Export
                        </Typography>
                        <Grid container spacing={2} className={classes.operationsGrid}>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/importLibraryToVersion"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <ImportIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Import Library
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
                        </Grid>
                    </div>
                </div>

                <div style={{ display: "flex", flexDirection: "row", gap: "16px" }}>
                    {/* Content Management Operations */}
                    <div className={classes.section}>
                        <Typography variant="h4" className={classes.sectionTitle}>
                            <StorageIcon /> Content Management
                        </Typography>
                        <Grid container spacing={2} className={classes.operationsGrid}>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/manageLibraries"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <LibraryIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Manage Libraries
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/manageUsecases"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <UseCaseIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Manage Use Cases
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/manageThreats"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <ThreatIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Manage Threats
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/manageWeaknesses"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <WeaknessIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Manage Weaknesses
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/manageControls"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <ControlIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Manage Controls
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/manageReferences"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <ReferenceIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Manage References
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/manageCategories"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <CategoryIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Manage Categories
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/manageStandards"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <StandardIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Manage Standards
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/manageSupportedStandards"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <StandardIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Manage Supported Standards
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            {/* <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/advancedRelationsCanvas"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <StandardIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Relation Editor
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid> */}
                        </Grid>
                    </div>
                    {/* Testing & Reports Operations */}
                    <div className={classes.section}>
                        <Typography variant="h4" className={classes.sectionTitle}>
                            <TestIcon /> Testing & Reports
                        </Typography>
                        <Grid container spacing={2} className={classes.operationsGrid}>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/runContentTests"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <TestIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Run Content Tests
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea component={Link} to={"/version/" + version + "/createReports"}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <ReportIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Create Reports
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                            <Grid item xs={12} sm={6} md={4}>
                                <Card className={classes.groupedOperationCard}>
                                    <CardActionArea onClick={fixNonASCIIValues}>
                                        <CardContent className={classes.groupedOperationContent}>
                                            <CodeIcon className={classes.operationIcon} />
                                            <Typography className={classes.operationTitle}>
                                                Fix Non-ASCII Values
                                            </Typography>
                                        </CardContent>
                                    </CardActionArea>
                                </Card>
                            </Grid>
                        </Grid>
                    </div>
                </div>

                <Divider className={classes.divider} />

                {/* Libraries Section */}
                <div className={classes.section}>
                    <Typography variant="h4" className={classes.sectionTitle}>
                        <LibraryIcon /> Libraries
                    </Typography>
                    <Grid container spacing={2} className={classes.librariesGrid}>
                        {sortedLibraryReport.map((value, index) => (
                            <Grid key={index} item xs={12} sm={6} md={4} lg={3}>
                                <SimpleCard
                                    className={classes.libraryCard}
                                    color="yellow"
                                    delete={deleteLibrary}
                                    download={exportLibraryToXML}
                                    revision={incrementRevision}
                                    title={value.libraryRef + " (" + value.revision + ")"}
                                    subtitle={"Threats: " + value.numThreats}
                                    subtitle2={"Rules: " + value.numRules}
                                    subtitle3={"Components: " + value.numComponentDefinitions}
                                    subtitle4={"Risk Patterns: " + value.numRiskPatterns}
                                    link={"/version/" + version + "/" + value.libraryRef}
                                />
                            </Grid>
                        ))}
                        <Grid item xs={12} sm={6} md={4} lg={3}>
                            <Link to={"/version/" + version + "/manageLibraries"} style={{ textDecoration: 'none' }}>
                                <Paper className={classes.addLibraryButton} elevation={1}>
                                    <Box display="flex" flexDirection="column" alignItems="center">
                                        <AddIcon style={{ fontSize: 32, color: '#667eea', marginBottom: 4 }} />
                                        <Typography variant="subtitle1" color="primary">
                                            Add Library
                                        </Typography>
                                    </Box>
                                </Paper>
                            </Link>
                        </Grid>
                    </Grid>
                </div>
            </Container>
        </div>
    );
};

export default Version;