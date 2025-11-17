import React, { lazy, Suspense, useEffect, useState, useCallback, useContext } from 'react';
import ReactDOM from 'react-dom';
import { HashRouter, NavLink, Route, Switch, useHistory } from "react-router-dom";
import clsx from 'clsx';
import * as serviceWorker from './serviceWorker';
import axios from 'axios';
import 'react-toastify/dist/ReactToastify.min.css';
import { ToastContainer } from 'react-toastify';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Drawer from '@material-ui/core/Drawer';
import Box from '@material-ui/core/Box';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import Container from '@material-ui/core/Container';
import IconButton from '@material-ui/core/IconButton';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import Logo from './assets/logo_icm.png';
import LogoBlack from './assets/logo_icm_black.png';
import Collapse from "@material-ui/core/Collapse";
import Button from "@material-ui/core/Button";
import { ChevronLeft, Menu } from '@material-ui/icons';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import AssignmentIcon from '@material-ui/icons/Assignment';
import CollectionsBookmarkIcon from '@material-ui/icons/CollectionsBookmark';
import Store from '@material-ui/icons/Store';
import DoubleArrowIcon from '@material-ui/icons/DoubleArrow';
import HomeIcon from '@material-ui/icons/Home';
import SimpleCard from "./components/utils/SimpleCard";
import { GreenButton } from "./components/utils/commonFunctions";
import { easyToast, failedToast } from "./components/utils/toastFunctions";
import { Menu as ContextMenu, Item, useContextMenu } from 'react-contexify';
import 'react-contexify/dist/ReactContexify.css';
import TextField from "@material-ui/core/TextField";
import AddCircleIcon from "@material-ui/icons/AddCircle";
import { ActivityIndicatorContext } from './components/utils/ActivityIndicatorContext';
import Marketplace from './components/marketplace/Marketplace';
import ManageReleaseNotes from './components/marketplace/operations/ManageReleaseNotes';
import './index.css';

// This components are loaded in this way to do code-splitting
const Library = lazy(() => import('./components/library/Library'));
const Project = lazy(() => import('./components/project/Project'));
const Version = lazy(() => import('./components/version/Version'));
const CreateProject = lazy(() => import('./components/project/operations/CreateProject'));
const LoadProject = lazy(() => import('./components/project/operations/LoadProject'));
const ManageVersion = lazy(() => import('./components/project/operations/ManageVersion'));
const ImportLibraryToVersion = lazy(() => import('./components/version/operations/ImportLibraryToVersion'));
const CreateRulesGraph = lazy(() => import('./components/library/operations/CreateRulesGraph'));
const CreateChangelogBetweenLibraries = lazy(() => import('./components/project/operations/CreateChangelogBetweenLibraries'));
const CreateChangelogBetweenVersions = lazy(() => import('./components/project/operations/CreateChangelogBetweenVersions'));
const ManageReferences = lazy(() => import('./components/version/operations/ManageReferences'));
const ManageLibraries = lazy(() => import('./components/version/operations/ManageLibraries'));
const ManageCategories = lazy(() => import('./components/version/operations/ManageCategories'));
const ManageComponents = lazy(() => import('./components/library/operations/ManageComponents'));
const ManageControls = lazy(() => import('./components/version/operations/ManageControls'));
const CreateElements = lazy(() => import('./components/version/operations/CreateElements'));
const ManageWeaknesses = lazy(() => import('./components/version/operations/ManageWeaknesses'));
const ManageThreats = lazy(() => import('./components/version/operations/ManageThreats'));
const CleanVersion = lazy(() => import("./components/version/operations/CleanVersion"));
const ManageUsecases = lazy(() => import('./components/version/operations/ManageUsecases'));
const SetMitigationValues = lazy(() => import('./components/library/operations/SetMitigationValues'));
const ManageRelations = lazy(() => import('./components/library/operations/ManageRelations'));
const ManageRiskPatterns = lazy(() => import('./components/library/operations/ManageRiskPatterns'));
const ManageStandards = lazy(() => import('./components/version/operations/ManageStandards'));
const ManageSupportedStandards = lazy(() => import('./components/version/operations/ManageSupportedStandards'));
const MergeLibraries = lazy(() => import('./components/project/operations/MergeLibraries'));
const RunContentTests = lazy(() => import('./components/version/operations/RunContentTests'));
const CleanFolders = lazy(() => import('./components/project/operations/CleanFolders'));
const CreateReports = lazy(() => import('./components/version/operations/CreateReports'));
const AdvancedRelationCanvas = lazy(() => import('./components/version/operations/AdvancedRelationCanvas'));

// Constants
const DRAWER_WIDTH = 240;
const IRIUSRISK_LIBRARY_EDITOR_VERSION = "1.0";
const MENU_ID = '1234567890';

// ActivityIndicator Provider Component
const ActivityIndicatorProvider = ({ children }) => {
  const [isVisible, setIsVisible] = useState(false);

  const show = useCallback(() => {
    setIsVisible(true);
  }, []);

  const hide = useCallback(() => {
    setIsVisible(false);
  }, []);

  return (
    <ActivityIndicatorContext.Provider value={{ show, hide }}>
      {children}
      <ActivityIndicator isVisible={isVisible} />
    </ActivityIndicatorContext.Provider>
  );
};

// ActivityIndicator Component
const ActivityIndicator = ({ isVisible }) => {
  useEffect(() => {
    // Inject keyframes if not already present
    if (!document.getElementById('spinner-keyframes')) {
      const style = document.createElement('style');
      style.id = 'spinner-keyframes';
      style.textContent = `
        @keyframes spinner-spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `;
      document.head.appendChild(style);
    }
  }, []);

  if (!isVisible) return null;

  return (
    <Box
      style={{
        position: 'fixed',
        top: '80px',
        right: '24px',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        padding: '12px 20px',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
      }}
    >
      <div
        style={{
          width: '20px',
          height: '20px',
          border: '3px solid #f3f3f3',
          borderTop: '3px solid #01ecb4',
          borderRadius: '50%',
          animation: 'spinner-spin 1s linear infinite',
        }}
      ></div>
      <Typography variant="body2" style={{ color: '#333', fontWeight: 500 }}>
        Processing...
      </Typography>
    </Box>
  );
};

// Hook to use ActivityIndicator
export const useActivityIndicator = () => {
  const context = useContext(ActivityIndicatorContext);
  if (!context) {
    // Return default functions if context is not available
    return { show: () => {}, hide: () => {} };
  }
  return context;
};

// Styles
const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    fontFamily: [
      'Overpass',
      'sans-serif'
    ].join(',')
  },
  toolbar: {
    //backgroundColor: "#16afa2",
    background: 'radial-gradient(80.88% 80.88% at 50% -20.37%, #01ecb480 0%, #01ecb41a 64.45%, #01ecb400 100%), linear-gradient(#305150 0%, #091c2c .01%)',
    //backgroundImage: `url(${Background2})`,
    paddingRight: 24, // keep right padding when drawer closed
    color: '#ffffff',
  },
  toolbarIcon: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: '0 8px',
    ...theme.mixins.toolbar,
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  },
  appBarShift: {
    marginLeft: DRAWER_WIDTH,
    width: `calc(100% - ${DRAWER_WIDTH}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  menuButton: {
    marginRight: 36,
    color: "#ffffff"
  },
  menuButtonHidden: {
    display: 'none',
  },
  menuButtonSelected: {
    backgroundColor: "#009aff29",
  },
  title: {
    flexGrow: 1,
    color: "#ffffff"
  },
  project: {
    color: "#ffffff",
    paddingRight: "10px"
  },
  drawerPaper: {
    position: 'relative',
    whiteSpace: 'nowrap',
    width: DRAWER_WIDTH,
    background: 'radial-gradient(80.88% 80.88% at 50% -20.37%, #01ecb480 0%, #01ecb41a 64.45%, #01ecb400 100%), linear-gradient(#305150 0%, #091c2c .01%)',
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
    // backgroundColor: "#edf2fa"
    color: '#ffffff',
  },
  drawerPaperClose: {
    overflowX: 'hidden',
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    width: theme.spacing(7),
    [theme.breakpoints.up('sm')]: {
      width: theme.spacing(9),
    },
  },
  appBarSpacer: {
    color: 'white'
  },
  content: {
    flexGrow: 1,
    height: '100vh',
    overflow: 'auto',
    background: 'radial-gradient(80.88% 80.88% at 50% -20.37%, #01ecb480 0%, #01ecb41a 64.45%, #01ecb400 100%), linear-gradient(#305150 0%, #091c2c .01%)'
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
    maxWidth: 'none'
  },
  paper: {
    padding: theme.spacing(2),
    display: 'flex',
    overflow: 'auto',
    flexDirection: 'column',
  },
  paperFixedHeight: {
    height: 150,
  },
  fixedHeight: {
    height: 240,
  },
  textfield: {
    padding: "15px",
    '& .MuiInputBase-input': {
      color: 'white',
    },
    '& .MuiInputLabel-root': {
      color: 'rgba(255, 255, 255, 0.7)',
    },
    '& .MuiInputLabel-root.Mui-focused': {
      color: 'white',
    },
    '& .MuiOutlinedInput-root': {
      '& fieldset': {
        borderColor: 'rgba(255, 255, 255, 0.3)',
      },
      '&:hover fieldset': {
        borderColor: 'rgba(255, 255, 255, 0.5)',
      },
      '&.Mui-focused fieldset': {
        borderColor: 'white',
      },
    },
  },
  addButton: {
    color: "#000000de"
  }
}));

// Custom hook for project state management
const useProjectState = () => {
  const [project, setProject] = useState("");
  const [versions, setVersions] = useState([]);

  const handleProjectChange = useCallback((newProject, newVersions) => {
    setProject(newProject);
    setVersions(newVersions);
  }, []);

  const loadProjectData = useCallback(async () => {
    try {
      const res = await axios.get('/api/project/versions');
      if (res.data.versions.length !== 0) {
        handleProjectChange(res.data.project, res.data.versions);
      }
    } catch (err) {
      failedToast(err);
    }
  }, [handleProjectChange]);

  return {
    project,
    versions,
    handleProjectChange,
    loadProjectData
  };
};

// Custom hook for drawer state management
const useDrawerState = () => {
  const [open, setOpen] = useState(true);
  const [openVersions, setOpenVersions] = useState(true);

  const toggleDrawer = useCallback(() => {
    setOpen(prev => !prev);
  }, []);

  const handleCollapseVersions = useCallback(() => {
    setOpenVersions(prev => !prev);
  }, []);

  return {
    open,
    openVersions,
    toggleDrawer,
    handleCollapseVersions
  };
};

// Custom hook for version management
const useVersionManagement = (handleProjectChange) => {
  const [newVersion, setNewVersion] = useState("");
  const history = useHistory();

  const handleItemClickRemove = useCallback(async ({ event, props }) => {
    try {
      const res = await axios.delete('/api/project/version/' + props.key);
      easyToast(res, "Version deleted successfully", "Deleting version failed");
      if (res.status === 200) {
        handleProjectChange(res.data.project, res.data.versions);
      }
    } catch (err) {
      failedToast("Deleting version failed: " + err);
    }
    event.preventDefault();
  }, [handleProjectChange]);

  const handleItemClickCopy = useCallback(async ({ event, props }) => {
    if (newVersion !== "") {
      try {
        const postData = {
          "src_version": props.key,
          "ref": newVersion
        };
        const res = await axios.post('/api/project/version/' + props.key + '/copy', postData);
        easyToast(res, "Version copied successfully", "Copying version failed");
        if (res.status === 200) {
          handleProjectChange(res.data.project, res.data.versions);
        }
      } catch (err) {
        failedToast("Copying version failed: " + err);
      }
    } else {
      failedToast("No version name defined");
    }
    event.preventDefault();
  }, [newVersion, handleProjectChange]);

  const handleItemClickQuickReload = useCallback(async ({ event, props }) => {
    try {
      const res = await axios.get('/api/version/' + props.key + '/quickreload');
      easyToast(res, "Quick reload done successfully", "Quick reload failed");
      if (res.status === 200) {
        const projectRes = await axios.get('/api/project/versions');
        handleProjectChange(projectRes.data.project, projectRes.data.versions);
      }
    } catch (err) {
      failedToast("Quick reload failed: " + err);
    }
    event.preventDefault();
  }, [handleProjectChange]);

  const handleItemClickNew = useCallback(async () => {
    if (newVersion !== "") {
      try {
        const res = await axios.post('/api/project/version/' + newVersion);
        easyToast(res, "Version created successfully", "Creating version failed");
        if (res.status === 200) {
          handleProjectChange(res.data.project, res.data.versions);
          history.push('/version/' + newVersion);
        }
      } catch (err) {
        failedToast("Creating version failed: " + err);
      }
    } else {
      failedToast("No version name defined");
    }
  }, [newVersion, handleProjectChange, history]);

  return {
    newVersion,
    setNewVersion,
    handleItemClickRemove,
    handleItemClickCopy,
    handleItemClickQuickReload,
    handleItemClickNew
  };
};

// Custom hook for project actions
const useProjectActions = (project, handleProjectChange) => {
  const { show, hide } = useActivityIndicator();

  const save = useCallback(async () => {
    show();
    try {
      const res = await axios.get('/api/project/save');
      easyToast(res, "Project saved successfully", "Saving project failed");
    } catch (err) {
      failedToast("Saving project failed: " + err);
    } finally {
      hide();
    }
  }, [show, hide]);

  const restore = useCallback(async () => {
    show();
    try {
      const res = await axios.get('/api/project/load/' + project);
      easyToast(res, "Project restored successfully", "Restoring project failed");
    } catch (err) {
      failedToast("Restoring project failed: " + err);
    } finally {
      hide();
    }
  }, [project, show, hide]);

  return { save, restore };
};

// Home component
const Home = () => {
  const classes = useStyles();
  const [projectStatus, setProjectStatus] = useState({ project: "", versions: [] });

  useEffect(() => {
    // Load current project status
    axios.get('/api/project/versions')
      .then(res => {
        if (res.data.versions.length > 0) {
          setProjectStatus(res.data);
        }
      })
      .catch(err => {
        // Project not loaded, that's fine
      });
  }, []);

  const getQuickActionCards = () => {
    if (projectStatus.project === "") {
      return [
        {
          title: "Create New Project",
          subtitle: "Start a new security library project",
          icon: "📁",
          link: "/project/createProject",
          color: "green"
        },
        {
          title: "Load Existing Project", 
          subtitle: "Continue working on a saved project",
          icon: "📂",
          link: "/project/loadProject",
          color: "blue"
        }
      ];
    } else {
      return [
        {
          title: "Manage Versions",
          subtitle: `Current project: ${projectStatus.project}`,
          icon: "🔄",
          link: "/project/manageVersion",
          color: "blue"
        },
        {
          title: "Export Project",
          subtitle: "Save your current work",
          icon: "💾",
          link: "/project",
          color: "yellow"
        },
        {
          title: "Create New Project",
          subtitle: "Start a new security library project",
          icon: "📁",
          link: "/project/createProject",
          color: "green"
        },
        {
          title: "Load Existing Project", 
          subtitle: "Continue working on a saved project",
          icon: "📂",
          link: "/project/loadProject",
          color: "blue"
        }
      ];
    }
  };

  const getFeatureCards = () => [
    {
      title: "Library Management",
      subtitle: "Create and manage security libraries",
      description: "Define risk patterns, components, and relationships",
      icon: "📚",
      link: projectStatus.project ? "/project" : null
    },
    {
      title: "Version Control", 
      subtitle: "Track changes across versions",
      description: "Compare versions and generate changelogs",
      icon: "📋",
      link: projectStatus.project ? "/project" : null
    },
    {
      title: "Security Elements",
      subtitle: "Manage threats, weaknesses, and controls",
      description: "Define comprehensive security frameworks",
      icon: "🛡️",
      link: projectStatus.project ? "/project" : null
    },
    {
      title: "Reports & Analytics",
      subtitle: "Generate detailed security reports",
      description: "Export to XML/XLSX and create statistics",
      icon: "📊",
      link: projectStatus.project ? "/project" : null
    }
  ];

  return (
    <div style={{ marginTop: '50px' }}>
      {/* Hero Section */}
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <img src={LogoBlack} alt="logo" style={{ width: 'auto', height: '100px' }} />

        <Typography variant="h6" style={{ color: 'rgba(0,0,0,0.8)', marginBottom: '20px' }}>
          {projectStatus.project 
            ? `Working on project: ${projectStatus.project} (${projectStatus.versions.length} versions)`
            : "Create or load a project to get started"
          }
        </Typography>
      </div>

      {/* Quick Actions */}
      <Typography variant="h5" style={{ color: 'black', marginBottom: '20px' }}>
        Quick Actions
      </Typography>
      <Grid container spacing={3} style={{ marginBottom: '40px' }}>
        {getQuickActionCards().map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <SimpleCard 
              title={card.title}
              subtitle={card.subtitle}
              link={card.link}
              color={card.color}
            />
          </Grid>
        ))}
      </Grid>

      {/* Features Overview */}
      <Typography variant="h5" style={{ color: 'black', marginBottom: '20px' }}>
        What You Can Do
      </Typography>
      <Grid container spacing={3} style={{ marginBottom: '40px' }}>
        {getFeatureCards().map((feature, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Paper 
              className={classes.paper} 
              elevation={3}
              style={{ 
                height: '200px', 
                display: 'flex', 
                flexDirection: 'column',
                justifyContent: 'space-between',
                backgroundColor: 'rgba(255,255,255,0.9)',
                color: 'black',
                border: '1px solid rgba(0,0,0,0.2)'
              }}
            >
              <div>
                <Typography variant="h4" style={{ marginBottom: '10px' }}>
                  {feature.icon}
                </Typography>
                <Typography variant="h6" style={{ marginBottom: '5px' }}>
                  {feature.title}
                </Typography>
                <Typography variant="subtitle1" style={{ color: 'rgba(0,0,0,0.8)', marginBottom: '10px' }}>
                  {feature.subtitle}
                </Typography>
                <Typography variant="body2" style={{ color: 'rgba(0,0,0,0.7)' }}>
                  {feature.description}
                </Typography>
              </div>
              {!feature.link && (
                <Typography variant="caption" style={{ color: 'rgba(0,0,0,0.5)' }}>
                  Load a project to access this feature
                </Typography>
              )}
            </Paper>
          </Grid>
        ))}
      </Grid>

    </div>
  );
};

// Router component
const AppRouter = ({ handleProjectChange, project }) => {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Switch>
        <Route path="/project/createChangelogBetweenVersions" render={() => <CreateChangelogBetweenVersions />} />
        <Route path="/project/createChangelogBetweenLibraries" render={() => <CreateChangelogBetweenLibraries />} />
        <Route path="/project/mergeLibraries" render={() => <MergeLibraries />} />
        <Route path="/project/cleanFolders" render={() => <CleanFolders />} />
        <Route path="/project/manageVersion" render={() => <ManageVersion handleProjectChange={handleProjectChange} />} />
        <Route path="/project/createProject" render={() => <CreateProject handleProjectChange={handleProjectChange} />} />
        <Route path="/project/loadProject" render={() => <LoadProject handleProjectChange={handleProjectChange} />} />
        <Route path="/project" render={() => <Project project={project} handleProjectChange={handleProjectChange} />} />
        <Route path="/version/:id/runContentTests" render={(props) => <RunContentTests version={props.match.params.id} />} />
        <Route path="/version/:id/cleanVersion" render={(props) => <CleanVersion version={props.match.params.id} />} />
        <Route path="/version/:id/importLibraryToVersion" render={(props) => <ImportLibraryToVersion version={props.match.params.id} />} />
        <Route path="/version/:id/manageUsecases" render={(props) => <ManageUsecases version={props.match.params.id} />} />
        <Route path="/version/:id/manageThreats" render={(props) => <ManageThreats version={props.match.params.id} />} />
        <Route path="/version/:id/manageWeaknesses" render={(props) => <ManageWeaknesses version={props.match.params.id} />} />
        <Route path="/version/:id/manageStandards" render={(props) => <ManageStandards version={props.match.params.id} />} />
        <Route path="/version/:id/manageSupportedStandards" render={(props) => <ManageSupportedStandards version={props.match.params.id} />} />
        <Route path="/version/:id/manageControls" render={(props) => <ManageControls version={props.match.params.id} />} />
        <Route path="/version/:id/createElements" render={(props) => <CreateElements version={props.match.params.id} />} />
        <Route path="/version/:id/manageCategories" render={(props) => <ManageCategories version={props.match.params.id} />} />
        <Route path="/version/:id/manageLibraries" render={(props) => <ManageLibraries version={props.match.params.id} />} />
        <Route path="/version/:id/manageReferences" render={(props) => <ManageReferences version={props.match.params.id} />} />
        <Route path="/version/:id/createReports" render={(props) => <CreateReports version={props.match.params.id} />} />
        <Route path="/version/:id/advancedRelationsCanvas" render={(props) => <AdvancedRelationCanvas version={props.match.params.id} />} />
        <Route path="/version/:id/:lib/setMitigationValues" render={(props) => <SetMitigationValues {...props} />} />
        <Route path="/version/:id/:lib/manageRiskPatterns" render={(props) => <ManageRiskPatterns {...props} />} />
        <Route path="/version/:id/:lib/manageRelations" render={(props) => <ManageRelations {...props} />} />
        <Route path="/version/:id/:lib/manageComponents" render={(props) => <ManageComponents {...props} />} />
        <Route path="/version/:id/:lib/rulesGraph" render={(props) => <CreateRulesGraph version={props.match.params.id} library={props.match.params.lib} />} />
        <Route path="/version/:id/:lib" render={(props) => <Library {...props} />} />
        <Route path="/version/:id" render={(props) => <Version {...props} />} />
        <Route path="/marketplace/manageReleaseNotes" render={(props) => <ManageReleaseNotes {...props} />} />
        <Route path="/marketplace" render={(props) => <Marketplace {...props} />} />
        <Route exact path="/" render={() => <Home />} />
      </Switch>
    </Suspense>
  );
};

// Main Dashboard component
const Dashboard = () => {
  const classes = useStyles();
  
  // Custom hooks
  const { project, versions, handleProjectChange, loadProjectData } = useProjectState();
  const { open, openVersions, toggleDrawer, handleCollapseVersions } = useDrawerState();
  const { setNewVersion, handleItemClickRemove, handleItemClickCopy, handleItemClickQuickReload, handleItemClickNew } = useVersionManagement(handleProjectChange);
  const { save, restore } = useProjectActions(project, handleProjectChange);

  // Context menu
  const { show } = useContextMenu({ id: MENU_ID });

  // Effects
  useEffect(() => {
    if (project === "") {
      loadProjectData();
    }
  }, [project, loadProjectData]);

  // Event handlers
  const handleContextMenu = useCallback((event, value) => {
    show(event, {
      props: {
        key: value
      }
    });
    event.preventDefault();
  }, [show]);

  return (
    <div className={classes.root}>
      <CssBaseline />
      <AppBar position="absolute" className={clsx(classes.appBar, open && classes.appBarShift)}>
        <Toolbar className={classes.toolbar}>
          <IconButton
            edge="start"
            aria-label="open drawer"
            onClick={toggleDrawer}
            className={clsx(classes.menuButton, open && classes.menuButtonHidden)}
          >
            <Menu />
          </IconButton>
          <img src={Logo} alt="logo" style={{ width: 'auto', height: '40px' }} />
          <Typography component="h1" variant="h6" color="inherit" noWrap className={classes.title}>
          </Typography>
          {project !== "" &&
            [
              <Typography key={1} variant="h6" className={classes.project}>
                Working on {project}
              </Typography>,
              <GreenButton key={2} variant="contained" color="primary" onClick={save}>Save</GreenButton>,
              <Button key={3} variant="contained" color="primary" onClick={restore}>Restore</Button>
            ]
          }
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        classes={{
          paper: clsx(classes.drawerPaper, !open && classes.drawerPaperClose),
        }}
        open={open}
      >
        <div className={classes.toolbarIcon}>
          <IconButton onClick={toggleDrawer}>
            <ChevronLeft style={{ color: 'white' }} />
          </IconButton>
        </div>
        <Divider />
        <ContextMenu id={MENU_ID}>
          <Item onClick={handleItemClickRemove}>Remove</Item>
          <Item onClick={handleItemClickCopy}>Copy</Item>
          <Item onClick={handleItemClickQuickReload}>Quick reload</Item>
        </ContextMenu>
        <List>
          <ListItem button component={NavLink} exact to="/" activeClassName={classes.menuButtonSelected}>
            <ListItemIcon>
              <HomeIcon style={{ color: 'white' }} />
            </ListItemIcon>
            <ListItemText primary="Home" />
          </ListItem>
          <ListItem button component={NavLink} to="/project" activeClassName={classes.menuButtonSelected}>
            <ListItemIcon>
              <AssignmentIcon  style={{ color: 'white' }} />
            </ListItemIcon>
            <ListItemText primary="Project" />
          </ListItem>
          <ListItem button component={NavLink} to="/marketplace" activeClassName={classes.menuButtonSelected}>
            <ListItemIcon>
              <Store style={{ color: 'white' }}/>
            </ListItemIcon>
            <ListItemText primary="Marketplace" />
          </ListItem>
          {project !== "" &&
            <div>
              <ListItem button onClick={handleCollapseVersions}>
                <ListItemIcon>
                  <CollectionsBookmarkIcon style={{ color: 'white' }}/>
                </ListItemIcon>
                <ListItemText primary="Versions" />
                {openVersions ? <ExpandLess style={{ color: 'white' }} /> : <ExpandMore style={{ color: 'white' }} />}
              </ListItem>
              <Collapse in={openVersions} timeout="auto" unmountOnExit>
                <List>
                  {versions.map((value, index) => {
                    return <ListItem key={index} button component={NavLink} to={"/version/" + value} activeClassName={classes.menuButtonSelected} onContextMenu={e => handleContextMenu(e, value)}>
                      <ListItemIcon>
                        <DoubleArrowIcon style={{ color: 'white' }} />
                      </ListItemIcon>
                      <ListItemText primary={value} />
                    </ListItem>
                  })}
                </List>
              </Collapse>
            </div>
          }
        </List>
        <TextField className={classes.textfield} id="newVersion" onBlur={e => setNewVersion(e.target.value)} />
        <IconButton aria-label="add" onClick={handleItemClickNew} >
          <AddCircleIcon className={classes.addButton} fontSize="large" style={{ color: 'white' }} />
        </IconButton>
      </Drawer>
      <main className={classes.content}>
        <div className={classes.appBarSpacer} />
        <Container className={classes.container}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Paper className={classes.paper}>
                <AppRouter handleProjectChange={handleProjectChange} project={project} />
              </Paper>
            </Grid>
          </Grid>
          <Box pt={4}>
            <Typography variant="body2" style={{ color: 'white' }} align="center">
              {'Copyright © '}
              <a href="https://iriusrisk.com//">
                IriusRisk
              </a>
              {' '}
              {new Date().getFullYear()}
              {'. Version '}
              {IRIUSRISK_LIBRARY_EDITOR_VERSION}
            </Typography>
          </Box>
        </Container>
      </main>
      <ToastContainer />
    </div>
  );
};

// ReactDOM Render
ReactDOM.render(
  <HashRouter>
    <ActivityIndicatorProvider>
      <Dashboard />
    </ActivityIndicatorProvider>
  </HashRouter>,
  document.getElementById('root')
);

serviceWorker.unregister();
