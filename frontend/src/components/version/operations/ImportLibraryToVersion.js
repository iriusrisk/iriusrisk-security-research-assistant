import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import UploadFiles from "../../utils/UploadFiles";
import Button from "@material-ui/core/Button";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import CardActions from "@material-ui/core/CardActions";
import Divider from "@material-ui/core/Divider";
import Box from "@material-ui/core/Box";
import Paper from "@material-ui/core/Paper";
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import FolderIcon from '@material-ui/icons/Folder';
import InfoIcon from '@material-ui/icons/Info';
import axios from "axios";
import {easyToast, failedToast} from "../../utils/toastFunctions";

const useStyles = makeStyles((theme) => ({
    root: {
      display: 'flex',
      minHeight: '100vh',
      backgroundColor: theme.palette.grey[50],
    },
    container: {
      paddingTop: theme.spacing(4),
      paddingBottom: theme.spacing(4),
    },
    header: {
      marginBottom: theme.spacing(4),
      textAlign: 'center',
    },
    section: {
      marginBottom: theme.spacing(4),
    },
    card: {
      marginBottom: theme.spacing(3),
      boxShadow: theme.shadows[2],
      borderRadius: theme.spacing(1),
      transition: 'box-shadow 0.3s ease-in-out',
      '&:hover': {
        boxShadow: theme.shadows[4],
      },
    },
    cardHeader: {
      display: 'flex',
      alignItems: 'center',
      marginBottom: theme.spacing(2),
    },
    cardIcon: {
      marginRight: theme.spacing(2),
      color: theme.palette.primary.main,
    },
    cardTitle: {
      fontWeight: 600,
      color: theme.palette.text.primary,
    },
    cardSubtitle: {
      color: theme.palette.text.secondary,
      marginTop: theme.spacing(1),
    },
    infoBox: {
      display: 'flex',
      alignItems: 'center',
      padding: theme.spacing(2),
      backgroundColor: theme.palette.info.light,
      borderRadius: theme.spacing(1),
      marginBottom: theme.spacing(2),
    },
    infoIcon: {
      marginRight: theme.spacing(1),
      color: theme.palette.info.main,
    },
    infoText: {
      color: theme.palette.info.contrastText,
      fontSize: '0.875rem',
    },
    button: {
      marginTop: theme.spacing(2),
      padding: theme.spacing(1.5, 3),
      borderRadius: theme.spacing(1),
      textTransform: 'none',
      fontWeight: 600,
    },
    divider: {
      margin: theme.spacing(3, 0),
    },
}));

const ImportLibraryToVersion = ({version}) => {
    const classes = useStyles();

    const handleSubmit = (event) => {
        axios.get("/api/version/"+version+"/import/folder")
            .then(res => {
                easyToast(res, "Imported libraries successfully", "Importing libraries failed");
            })
            .catch(err => failedToast("Importing libraries failed: "+err));

        event.preventDefault();
    };

    return(
        <div className={classes.root}>
          <CssBaseline />
          <Container maxWidth="md" className={classes.container}>
              <Box className={classes.header}>
                  <Typography variant="h3" component="h1" gutterBottom>
                      Import Library to Version
                  </Typography>
                  <Typography variant="h6" color="textSecondary">
                      Upload and manage libraries for version {version}
                  </Typography>
              </Box>

              <Paper elevation={0} style={{ padding: '24px', backgroundColor: 'transparent' }}>
                  {/* File Upload Section */}
                  <Card className={classes.card}>
                      <CardContent>
                          <Box className={classes.cardHeader}>
                              <CloudUploadIcon className={classes.cardIcon} fontSize="large" />
                              <Box>
                                  <Typography variant="h5" className={classes.cardTitle}>
                                      Upload Library Files
                                  </Typography>
                                  <Typography variant="body2" className={classes.cardSubtitle}>
                                      Upload library files directly to this version
                                  </Typography>
                              </Box>
                          </Box>
                          <UploadFiles version={version}/>
                      </CardContent>
                  </Card>

                  <Divider className={classes.divider} />

                  {/* Folder Import Section */}
                  <Card className={classes.card}>
                      <CardContent>
                          <Box className={classes.cardHeader}>
                              <FolderIcon className={classes.cardIcon} fontSize="large" />
                              <Box>
                                  <Typography variant="h5" className={classes.cardTitle}>
                                      Load Libraries from Folder
                                  </Typography>
                                  <Typography variant="body2" className={classes.cardSubtitle}>
                                      Import libraries from a configured folder location
                                  </Typography>
                              </Box>
                          </Box>
                          
                          <Box className={classes.infoBox}>
                              <InfoIcon className={classes.infoIcon} />
                              <Typography className={classes.infoText}>
                                  Remember to set a folder in "main-library-folder" in /config/user_config.properties
                              </Typography>
                          </Box>

                          <CardActions>
                              <Button 
                                  className={classes.button} 
                                  variant="contained" 
                                  color="primary" 
                                  onClick={handleSubmit}
                                  startIcon={<FolderIcon />}
                              >
                                  Load Libraries
                              </Button>
                          </CardActions>
                      </CardContent>
                  </Card>
              </Paper>
          </Container>
        </div>
    );
};

export default ImportLibraryToVersion;