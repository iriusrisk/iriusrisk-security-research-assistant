import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import Changelog from "./Changelog";
import AccordionSummary from "@material-ui/core/AccordionSummary";
import AccordionDetails from "@material-ui/core/AccordionDetails";
import Accordion from "@material-ui/core/Accordion";
import { failedToast, successToast, warnToast } from "../../utils/toastFunctions";
import Grid from "@material-ui/core/Grid";
import InputLabel from "@material-ui/core/InputLabel";
import Select from "@material-ui/core/Select";
import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import CircularProgress from "@material-ui/core/CircularProgress";
import Box from "@material-ui/core/Box";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import AddIcon from "@material-ui/icons/Add";
import DeleteIcon from "@material-ui/icons/Delete";
import EditIcon from "@material-ui/icons/Edit";
import Divider from "@material-ui/core/Divider";

const useStyles = (theme) => ({
    root: {
        display: 'flex',
    },
    container: {
        paddingTop: theme.spacing(4),
        paddingBottom: theme.spacing(4),
    },
    newItem: {
        backgroundColor: "#13e29d"
    },
    deletedItem: {
        backgroundColor: "#f97678"
    },
    editedItem: {
        backgroundColor: "#ffe381"
    },
    noChangedItem: {
        backgroundColor: "#cdf0ff"
    },
    newText: {
        color: "#13e29d"
    },
    deletedText: {
        color: "#f97678"
    },
    editedText: {
        color: "#ffe381"
    },
    paper: {
        padding: "20px",
        margin: "5px"
    },
    loadingContainer: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: theme.spacing(4),
    },
    buttonContainer: {
        marginTop: theme.spacing(2),
    },
    libraryList: {
        marginTop: theme.spacing(2),
    },
    libraryItem: {
        cursor: 'pointer',
        '&:hover': {
            backgroundColor: theme.palette.action.hover,
        },
    },
    sectionTitle: {
        marginTop: theme.spacing(2),
        marginBottom: theme.spacing(1),
        fontWeight: 'bold',
    }
});

const CreateChangelogBetweenVersions = (props) => {
    const { classes } = props;
    const [versions, setVersions] = useState([]);
    const [selectedVersionFirst, setSelectedVersionFirst] = useState("");
    const [selectedVersionSecond, setSelectedVersionSecond] = useState("");
    const [librarySummaries, setLibrarySummaries] = useState(null);
    const [selectedLibrary, setSelectedLibrary] = useState(null);
    const [libraryDetails, setLibraryDetails] = useState(null);
    const [expanded, setExpanded] = useState("");
    const [loading, setLoading] = useState(false);
    const [loadingLibrary, setLoadingLibrary] = useState(false);

    useEffect(() => {
        axios.get(`/project/versions`)
            .then(res => {
                if (res.data.versions.length > 0) {
                    setVersions(res.data.versions);
                    setSelectedVersionFirst(res.data.versions[0]);
                    setSelectedVersionSecond(res.data.versions[0]);
                }
            })
            .catch(err => failedToast(err));
    }, []);

    const handleChangeVersionFirst = useCallback((event) => {
        setSelectedVersionFirst(event.target.value);
        setLibrarySummaries(null);
        setSelectedLibrary(null);
        setLibraryDetails(null);
    }, []);

    const handleChangeVersionSecond = useCallback((event) => {
        setSelectedVersionSecond(event.target.value);
        setLibrarySummaries(null);
        setSelectedLibrary(null);
        setLibraryDetails(null);
    }, []);

    const fetchLibrarySummaries = useCallback(async () => {
        if (selectedVersionFirst === selectedVersionSecond) {
            warnToast("Both old and new versions are the same");
            return;
        }

        setLoading(true);
        const requestData = {
            "from_version": selectedVersionFirst,
            "to_version": selectedVersionSecond,
        };

        try {
            const response = await axios.post('/api/project/diff/versions/summaries', requestData);
            setLibrarySummaries(response.data);
            successToast("Library summaries loaded");
        } catch (error) {
            failedToast(`Failed to load library summaries: ${error}`);
        } finally {
            setLoading(false);
        }
    }, [selectedVersionFirst, selectedVersionSecond]);

    const fetchLibraryDetails = useCallback(async (libraryRef) => {
        setLoadingLibrary(true);
        const requestData = {
            "from_version": selectedVersionFirst,
            "to_version": selectedVersionSecond,
            "library_ref": libraryRef
        };

        try {
            const response = await axios.post('/api/project/diff/versions/library', requestData);
            setLibraryDetails(response.data);
            setSelectedLibrary(libraryRef);
            successToast("Library details loaded");
        } catch (error) {
            failedToast(`Failed to load library details: ${error}`);
        } finally {
            setLoadingLibrary(false);
        }
    }, [selectedVersionFirst, selectedVersionSecond]);

    const handleExpandAccordion = useCallback((panel) => (event, newExpanded) => {
        setExpanded(newExpanded ? panel : false);
    }, []);

    const getChangeIcon = (changeType) => {
        switch (changeType) {
            case "ADDED":
                return <AddIcon className={classes.newText} />;
            case "DELETED":
                return <DeleteIcon className={classes.deletedText} />;
            case "MODIFIED":
                return <EditIcon className={classes.editedText} />;
            default:
                return null;
        }
    };

    const getChangeText = (changeType) => {
        switch (changeType) {
            case "ADDED":
                return "Added";
            case "DELETED":
                return "Deleted";
            case "MODIFIED":
                return "Modified";
            default:
                return changeType;
        }
    };

    const totalChanges = useMemo(() => {
        if (!librarySummaries) return 0;
        return (librarySummaries.addedLibraries?.length || 0) +
               (librarySummaries.deletedLibraries?.length || 0) +
               (librarySummaries.modifiedLibraries?.length || 0);
    }, [librarySummaries]);

    return (
        <div className={classes.root}>
            <CssBaseline/>
            <Container maxWidth="lg" className={classes.container}>
                <div>
                    <Typography variant="h4">
                        Create Changelog Between Versions
                    </Typography>
                    <div>
                        <Paper className={classes.paper} elevation={3}>
                            <Grid container spacing={2}>
                                <Grid item xs={4}>
                                    <InputLabel>
                                        Old version
                                    </InputLabel>
                                    <Select
                                        native
                                        value={selectedVersionFirst}
                                        variant="outlined"
                                        onChange={handleChangeVersionFirst}
                                    >
                                        {versions.map((value, index) => (
                                            <option key={index} value={value}>{value}</option>
                                        ))}
                                    </Select>
                                </Grid>
                                <Grid item xs={4}>
                                    <InputLabel>
                                        New version
                                    </InputLabel>
                                    <Select
                                        native
                                        value={selectedVersionSecond}
                                        variant="outlined"
                                        onChange={handleChangeVersionSecond}
                                    >
                                        {versions.map((value, index) => (
                                            <option key={index} value={value}>{value}</option>
                                        ))}
                                    </Select>
                                </Grid>
                                <Grid item xs={4} className={classes.buttonContainer}>
                                    <Button 
                                        variant="contained" 
                                        color="primary" 
                                        onClick={fetchLibrarySummaries}
                                        disabled={loading}
                                        startIcon={loading ? <CircularProgress size={20} /> : null}
                                    >
                                        {loading ? 'Loading summaries...' : 'Get Library Changes'}
                                    </Button>
                                </Grid>
                            </Grid>
                        </Paper>

                        {loading && (
                            <Paper className={classes.paper} elevation={3}>
                                <Box className={classes.loadingContainer}>
                                    <CircularProgress />
                                    <Typography variant="h6" style={{ marginLeft: 16 }}>
                                        Loading library summaries...
                                    </Typography>
                                </Box>
                            </Paper>
                        )}

                        {librarySummaries && !loading && (
                            <Paper className={classes.paper} elevation={3}>
                                <Typography variant="h5">
                                    Library Changes ({totalChanges} total)
                                </Typography>
                                
                                <div className={classes.libraryList}>
                                    {librarySummaries.addedLibraries && librarySummaries.addedLibraries.length > 0 && (
                                        <div>
                                            <Typography variant="h6" className={classes.sectionTitle}>
                                                Added Libraries ({librarySummaries.addedLibraries.length})
                                            </Typography>
                                            <List>
                                                {librarySummaries.addedLibraries.map((library, index) => (
                                                    <ListItem 
                                                        key={`added-${index}`}
                                                        className={classes.libraryItem}
                                                        onClick={() => fetchLibraryDetails(library.library_ref)}
                                                    >
                                                        <ListItemIcon>
                                                            {getChangeIcon(library.changeType)}
                                                        </ListItemIcon>
                                                        <ListItemText 
                                                            primary={library.library_name}
                                                            secondary={`${getChangeText(library.changeType)} • Revision: ${library.newRevision}`}
                                                        />
                                                    </ListItem>
                                                ))}
                                            </List>
                                            <Divider />
                                        </div>
                                    )}

                                    {librarySummaries.deletedLibraries && librarySummaries.deletedLibraries.length > 0 && (
                                        <div>
                                            <Typography variant="h6" className={classes.sectionTitle}>
                                                Deleted Libraries ({librarySummaries.deletedLibraries.length})
                                            </Typography>
                                            <List>
                                                {librarySummaries.deletedLibraries.map((library, index) => (
                                                    <ListItem 
                                                        key={`deleted-${index}`}
                                                        className={classes.libraryItem}
                                                        onClick={() => fetchLibraryDetails(library.library_ref)}
                                                    >
                                                        <ListItemIcon>
                                                            {getChangeIcon(library.changeType)}
                                                        </ListItemIcon>
                                                        <ListItemText 
                                                            primary={library.library_name}
                                                            secondary={`${getChangeText(library.changeType)} • Revision: ${library.oldRevision}`}
                                                        />
                                                    </ListItem>
                                                ))}
                                            </List>
                                            <Divider />
                                        </div>
                                    )}

                                    {librarySummaries.modifiedLibraries && librarySummaries.modifiedLibraries.length > 0 && (
                                        <div>
                                            <Typography variant="h6" className={classes.sectionTitle}>
                                                Modified Libraries ({librarySummaries.modifiedLibraries.length})
                                            </Typography>
                                            <List>
                                                {librarySummaries.modifiedLibraries.map((library, index) => (
                                                    <ListItem 
                                                        key={`modified-${index}`}
                                                        className={classes.libraryItem}
                                                        onClick={() => fetchLibraryDetails(library.library_ref)}
                                                    >
                                                        <ListItemIcon>
                                                            {getChangeIcon(library.changeType)}
                                                        </ListItemIcon>
                                                        <ListItemText 
                                                            primary={library.library_name}
                                                            secondary={`${getChangeText(library.changeType)} • ${library.oldRevision} → ${library.newRevision}`}
                                                        />
                                                    </ListItem>
                                                ))}
                                            </List>
                                        </div>
                                    )}

                                    {totalChanges === 0 && (
                                        <Typography variant="body1" style={{ textAlign: 'center', padding: '20px' }}>
                                            No changes found between the selected versions.
                                        </Typography>
                                    )}
                                </div>
                            </Paper>
                        )}

                        {loadingLibrary && (
                            <Paper className={classes.paper} elevation={3}>
                                <Box className={classes.loadingContainer}>
                                    <CircularProgress />
                                    <Typography variant="h6" style={{ marginLeft: 16 }}>
                                        Loading library details...
                                    </Typography>
                                </Box>
                            </Paper>
                        )}

                        {libraryDetails && !loadingLibrary && selectedLibrary && (
                            <Paper className={classes.paper} elevation={3}>
                                <Typography variant="h5">
                                    Detailed Changes for {selectedLibrary}
                                </Typography>
                                <Changelog data={libraryDetails} noGraph={true} />
                            </Paper>
                        )}
                    </div>
                </div>
            </Container>
        </div>
    );
};

export default withStyles(useStyles)(CreateChangelogBetweenVersions);