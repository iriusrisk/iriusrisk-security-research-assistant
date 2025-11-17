import React, { useState, useEffect, useCallback } from 'react';
import { withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import { easyToast, failedToast, successToast } from "../../utils/toastFunctions";
import Paper from "@material-ui/core/Paper";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import IconButton from "@material-ui/core/IconButton";
import DeleteIcon from "@material-ui/icons/Delete";
import AddIcon from "@material-ui/icons/Add";
import SaveIcon from "@material-ui/icons/Save";
import FolderOpenIcon from "@material-ui/icons/FolderOpen";
import Accordion from "@material-ui/core/Accordion";
import AccordionSummary from "@material-ui/core/AccordionSummary";
import AccordionDetails from "@material-ui/core/AccordionDetails";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import Divider from "@material-ui/core/Divider";
import Dialog from "@material-ui/core/Dialog";
import DialogTitle from "@material-ui/core/DialogTitle";
import DialogContent from "@material-ui/core/DialogContent";
import DialogActions from "@material-ui/core/DialogActions";

const useStyles = (theme) => ({
    root: {
      display: 'flex',
    },
    container: {
      paddingTop: theme.spacing(4),
      paddingBottom: theme.spacing(4),
    },
    paper:{
        padding: "20px",
        margin: "5px"
    },
    button: {
        float: "right",
        margin: theme.spacing(1)
    },
    fileInput: {
        display: 'none'
    },
    section: {
        marginBottom: theme.spacing(3)
    },
    releaseNoteRow: {
        marginBottom: theme.spacing(2),
        padding: theme.spacing(2),
        border: '1px solid #e0e0e0',
        borderRadius: theme.spacing(1)
    },
    releaseNoteHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: theme.spacing(1)
    },
    textField: {
        marginBottom: theme.spacing(2)
    },
    actionButtons: {
        display: 'flex',
        gap: theme.spacing(1),
        marginTop: theme.spacing(2)
    }
});

const ManageReleaseNotes = (props) => {
    const { classes } = props;
    const [packages, setPackages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [basePath, setBasePath] = useState('');
    const [addReleaseNoteDialog, setAddReleaseNoteDialog] = useState({ open: false, packageIndex: null, revisionKey: '' });

    const handleFolderSelect = async (event) => {
        const files = Array.from(event.target.files);
        if (files.length === 0) return;

        setLoading(true);
        const summaryFiles = files.filter(file => file.name.endsWith('_summary.json'));
        
        if (summaryFiles.length === 0) {
            failedToast("No _summary.json files found in the selected folder");
            setLoading(false);
            return;
        }

        const loadedPackages = [];

        for (const file of summaryFiles) {
            try {
                const text = await readFileAsText(file);
                const jsonData = JSON.parse(text);
                
                // Extract the relative path from the file's webkitRelativePath
                const relativePath = file.webkitRelativePath || file.name;
                
                loadedPackages.push({
                    filePath: relativePath,
                    file: file,
                    data: jsonData,
                    libraryRef: jsonData.library?.ref || 'unknown',
                    libraryName: jsonData.library?.name || 'Unknown Library',
                    revision: jsonData.library?.revision || 0,
                    releaseNotes: jsonData.library?.releaseNotes || {}
                });
            } catch (error) {
                console.error(`Error reading file ${file.name}:`, error);
                failedToast(`Error reading file ${file.name}: ${error.message}`);
            }
        }

        setPackages(loadedPackages);
        setLoading(false);
        successToast(`Loaded ${loadedPackages.length} package(s)`);
    };

    const readFileAsText = (file) => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    };

    const updateLibraryProperty = useCallback((packageIndex, property, value) => {
        setPackages(prevPackages => {
            return prevPackages.map((pkg, idx) => {
                if (idx !== packageIndex) {
                    return pkg; // Return unchanged package - React will skip re-render
                }
                
                // Create a new package with updated library property
                const updatedLibrary = {
                    ...(pkg.data.library || {}),
                    [property]: value
                };
                
                const updatedData = {
                    ...pkg.data,
                    library: updatedLibrary
                };
                
                // Also update the cached values for display
                const updatedPkg = {
                    ...pkg,
                    data: updatedData
                };
                
                if (property === 'ref') updatedPkg.libraryRef = value;
                if (property === 'name') updatedPkg.libraryName = value;
                if (property === 'revision') updatedPkg.revision = value;
                
                return updatedPkg;
            });
        });
    }, []);

    const updateReleaseNote = useCallback((packageIndex, revision, field, value) => {
        setPackages(prevPackages => {
            return prevPackages.map((pkg, idx) => {
                if (idx !== packageIndex) {
                    return pkg; // Return unchanged package - React will skip re-render
                }
                
                // Create a new package object with updated release notes
                const updatedReleaseNotes = {
                    ...pkg.releaseNotes,
                    [revision]: {
                        ...(pkg.releaseNotes[revision] || { date: '', description: '' }),
                        [field]: value
                    }
                };
                
                return {
                    ...pkg,
                    releaseNotes: updatedReleaseNotes
                };
            });
        });
    }, []);

    const addCategory = (packageIndex) => {
        const updatedPackages = [...packages];
        const pkg = updatedPackages[packageIndex];
        
        if (!pkg.data.library) {
            pkg.data.library = {};
        }
        
        if (!pkg.data.library.categories) {
            pkg.data.library.categories = [];
        }
        
        pkg.data.library.categories.push({ ref: '' });
        setPackages(updatedPackages);
    };

    const updateCategory = (packageIndex, categoryIndex, ref) => {
        const updatedPackages = [...packages];
        const pkg = updatedPackages[packageIndex];
        
        if (!pkg.data.library) {
            pkg.data.library = {};
        }
        
        if (!pkg.data.library.categories) {
            pkg.data.library.categories = [];
        }
        
        if (pkg.data.library.categories[categoryIndex]) {
            pkg.data.library.categories[categoryIndex].ref = ref;
        }
        
        setPackages(updatedPackages);
    };

    const removeCategory = (packageIndex, categoryIndex) => {
        const updatedPackages = [...packages];
        const pkg = updatedPackages[packageIndex];
        
        if (pkg.data.library.categories) {
            pkg.data.library.categories.splice(categoryIndex, 1);
        }
        
        setPackages(updatedPackages);
    };

    const openAddReleaseNoteDialog = (packageIndex) => {
        const pkg = packages[packageIndex];
        // Get current revision from library data
        const currentRevision = pkg.data.library?.revision || pkg.revision || 0;
        
        // Find the next revision number as default
        const existingRevisions = Object.keys(pkg.releaseNotes).map(Number).filter(n => !isNaN(n));
        const nextRevision = existingRevisions.length > 0 ? Math.max(...existingRevisions) + 1 : currentRevision + 1;
        
        setAddReleaseNoteDialog({
            open: true,
            packageIndex: packageIndex,
            revisionKey: nextRevision.toString()
        });
    };

    const closeAddReleaseNoteDialog = () => {
        setAddReleaseNoteDialog({ open: false, packageIndex: null, revisionKey: '' });
    };

    const addReleaseNote = () => {
        if (!addReleaseNoteDialog.revisionKey || addReleaseNoteDialog.revisionKey.trim() === '') {
            failedToast("Please enter a valid revision key");
            return;
        }

        const updatedPackages = [...packages];
        const pkg = updatedPackages[addReleaseNoteDialog.packageIndex];
        
        // Check if revision key already exists
        if (pkg.releaseNotes[addReleaseNoteDialog.revisionKey]) {
            failedToast(`Release note with key "${addReleaseNoteDialog.revisionKey}" already exists`);
            return;
        }
        
        pkg.releaseNotes[addReleaseNoteDialog.revisionKey] = {
            date: new Date().toISOString().split('T')[0], // Today's date in YYYY-MM-DD format
            description: ''
        };
        
        setPackages(updatedPackages);
        closeAddReleaseNoteDialog();
    };

    const deleteReleaseNote = (packageIndex, revision) => {
        const updatedPackages = [...packages];
        const pkg = updatedPackages[packageIndex];
        delete pkg.releaseNotes[revision];
        setPackages(updatedPackages);
    };

    const prepareFileData = (pkg) => {
        return {
            filePath: pkg.filePath,
            data: {
                ...pkg.data,
                library: {
                    ...pkg.data.library,
                    releaseNotes: pkg.releaseNotes
                }
            }
        };
    };

    const saveSingleFile = async (packageIndex) => {
        const pkg = packages[packageIndex];
        if (!pkg) {
            failedToast("Package not found");
            return;
        }

        setLoading(true);
        
        try {
            const fileToSave = prepareFileData(pkg);

            // Call backend API to save file
            const response = await axios.post('/api/marketplace/save-release-notes', {
                files: [fileToSave],
                basePath: basePath || undefined
            });

            if (response.status === 200) {
                successToast(`Successfully saved ${pkg.libraryName || pkg.filePath}`);
            } else {
                failedToast("Failed to save file");
            }
        } catch (error) {
            console.error('Error saving file:', error);
            failedToast(`Error saving file: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const saveAllFiles = async () => {
        if (packages.length === 0) {
            failedToast("No packages to save");
            return;
        }

        setLoading(true);
        
        try {
            // Prepare the data to send to the backend
            const filesToSave = packages.map(pkg => prepareFileData(pkg));

            // Call backend API to save files
            const response = await axios.post('/api/marketplace/save-release-notes', {
                files: filesToSave,
                basePath: basePath || undefined
            });

            if (response.status === 200) {
                successToast(`Successfully saved ${packages.length} file(s)`);
            } else {
                failedToast("Failed to save files");
            }
        } catch (error) {
            console.error('Error saving files:', error);
            failedToast(`Error saving files: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const getReleaseNoteRevisions = (pkg) => {
        return Object.keys(pkg.releaseNotes).sort((a, b) => {
            const numA = parseInt(a);
            const numB = parseInt(b);
            if (!isNaN(numA) && !isNaN(numB)) {
                return numB - numA; // Sort descending
            }
            return a.localeCompare(b);
        });
    };

    return (
        <div className={classes.root}>
          <CssBaseline />
          <Container maxWidth="lg" className={classes.container}>
              <div>
                  <Typography variant="h4" gutterBottom>
                      Manage Release Notes
                  </Typography>
                  
                  <Paper className={classes.paper} elevation={3}>
                      <div className={classes.section}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' }}>
                              <input
                                  accept=".json"
                                  className={classes.fileInput}
                                  id="folder-input"
                                  type="file"
                                  webkitdirectory=""
                                  directory=""
                                  multiple
                                  onChange={handleFolderSelect}
                              />
                              <label htmlFor="folder-input">
                                  <Button
                                      variant="contained"
                                      color="primary"
                                      component="span"
                                      startIcon={<FolderOpenIcon />}
                                      disabled={loading}
                                  >
                                      Select Folder
                                  </Button>
                              </label>
                              
                              {packages.length > 0 && (
                                  <Button
                                      variant="contained"
                                      color="secondary"
                                      startIcon={<SaveIcon />}
                                      onClick={saveAllFiles}
                                      disabled={loading}
                                  >
                                      Save All Files
                                  </Button>
                              )}
                          </div>
                          
                          {packages.length > 0 && (
                              <TextField
                                  label="Base Path for Saving (optional)"
                                  variant="outlined"
                                  fullWidth
                                  value={basePath}
                                  onChange={(e) => setBasePath(e.target.value)}
                                  placeholder="e.g., C:/path/to/folder (leave empty to save to default output folder)"
                                  helperText="Specify the base folder path where files should be saved. Leave empty to save to the default output folder. The relative path structure will be preserved."
                                  style={{ marginBottom: '10px' }}
                              />
                          )}
                      </div>

                      {loading && (
                          <Typography variant="body1" color="textSecondary">
                              Loading files...
                          </Typography>
                      )}

                      {packages.length > 0 && (
                          <div>
                              <Typography variant="h6" gutterBottom>
                                  Loaded Packages ({packages.length})
                              </Typography>
                              
                              {packages.map((pkg, packageIndex) => (
                                  <Accordion key={packageIndex} defaultExpanded={packageIndex === 0}>
                                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', marginRight: '16px' }}>
                                              <div>
                                                  <Typography variant="h6">
                                                      {pkg.data.library?.name || pkg.libraryName || 'Unknown Library'} ({pkg.data.library?.ref || pkg.libraryRef || 'unknown'})
                                                  </Typography>
                                                  <Typography variant="body2" style={{ color: '#666' }}>
                                                      Path: {pkg.filePath} | Revision: {pkg.data.library?.revision || pkg.revision || 0}
                                                  </Typography>
                                              </div>
                                              <Button
                                                  variant="contained"
                                                  color="primary"
                                                  size="small"
                                                  startIcon={<SaveIcon />}
                                                  onClick={(e) => {
                                                      e.stopPropagation();
                                                      saveSingleFile(packageIndex);
                                                  }}
                                                  disabled={loading}
                                              >
                                                  Save
                                              </Button>
                                          </div>
                                      </AccordionSummary>
                                      <AccordionDetails>
                                          <div style={{ width: '100%' }}>
                                              {/* Library Properties Section */}
                                              <Paper elevation={1} style={{ padding: '16px', marginBottom: '20px', backgroundColor: '#f5f5f5' }}>
                                                  <Typography variant="h6" gutterBottom>
                                                      Library Properties
                                                  </Typography>
                                                  
                                                  <TextField
                                                      label="Library Reference"
                                                      variant="outlined"
                                                      fullWidth
                                                      className={classes.textField}
                                                      value={pkg.data.library?.ref || ''}
                                                      onChange={(e) => updateLibraryProperty(packageIndex, 'ref', e.target.value)}
                                                      helperText="Unique identifier for the library"
                                                  />
                                                  
                                                  <TextField
                                                      label="Library Name"
                                                      variant="outlined"
                                                      fullWidth
                                                      className={classes.textField}
                                                      value={pkg.data.library?.name || ''}
                                                      onChange={(e) => updateLibraryProperty(packageIndex, 'name', e.target.value)}
                                                      helperText="Display name of the library"
                                                  />
                                                  
                                                  <TextField
                                                      label="Revision"
                                                      variant="outlined"
                                                      type="number"
                                                      fullWidth
                                                      className={classes.textField}
                                                      value={pkg.data.library?.revision || 0}
                                                      onChange={(e) => updateLibraryProperty(packageIndex, 'revision', parseInt(e.target.value) || 0)}
                                                      helperText="Current revision number"
                                                      InputProps={{
                                                          inputProps: { min: 0 }
                                                      }}
                                                  />
                                                  
                                                  <TextField
                                                      label="Description"
                                                      variant="outlined"
                                                      fullWidth
                                                      multiline
                                                      rows={3}
                                                      className={classes.textField}
                                                      value={pkg.data.library?.desc || ''}
                                                      onChange={(e) => updateLibraryProperty(packageIndex, 'desc', e.target.value)}
                                                      helperText="Library description"
                                                  />
                                                  
                                                  <div style={{ marginTop: '16px' }}>
                                                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                                                          <Typography variant="subtitle2">
                                                              Categories
                                                          </Typography>
                                                          <Button
                                                              variant="outlined"
                                                              color="primary"
                                                              size="small"
                                                              startIcon={<AddIcon />}
                                                              onClick={() => addCategory(packageIndex)}
                                                          >
                                                              Add Category
                                                          </Button>
                                                      </div>
                                                      
                                                      {(!pkg.data.library?.categories || pkg.data.library.categories.length === 0) ? (
                                                          <Typography variant="body2" color="textSecondary" style={{ marginBottom: '8px' }}>
                                                              No categories. Click "Add Category" to add one.
                                                          </Typography>
                                                      ) : (
                                                          pkg.data.library.categories.map((category, categoryIndex) => (
                                                              <div key={categoryIndex} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                                                                  <TextField
                                                                      label={`Category ${categoryIndex + 1} Reference`}
                                                                      variant="outlined"
                                                                      size="small"
                                                                      fullWidth
                                                                      value={category.ref || ''}
                                                                      onChange={(e) => updateCategory(packageIndex, categoryIndex, e.target.value)}
                                                                      placeholder="Enter category reference"
                                                                  />
                                                                  <IconButton
                                                                      size="small"
                                                                      color="secondary"
                                                                      onClick={() => removeCategory(packageIndex, categoryIndex)}
                                                                  >
                                                                      <DeleteIcon />
                                                                  </IconButton>
                                                              </div>
                                                          ))
                                                      )}
                                                  </div>
                                              </Paper>

                                              <Divider style={{ margin: '20px 0' }} />

                                              {/* Release Notes Section */}
                                              <div style={{ marginBottom: '16px' }}>
                                                  <Typography variant="h6" gutterBottom>
                                                      Release Notes
                                                  </Typography>
                                                  <Button
                                                      variant="outlined"
                                                      color="primary"
                                                      size="small"
                                                      startIcon={<AddIcon />}
                                                      onClick={() => openAddReleaseNoteDialog(packageIndex)}
                                                      style={{ marginBottom: '16px' }}
                                                  >
                                                      Add Release Note
                                                  </Button>
                                              </div>

                                              {getReleaseNoteRevisions(pkg).length === 0 ? (
                                                  <Typography variant="body2" color="textSecondary">
                                                      No release notes found. Click "Add Release Note" to create one.
                                                  </Typography>
                                              ) : (
                                                  getReleaseNoteRevisions(pkg).map((revision) => {
                                                      const releaseNote = pkg.releaseNotes[revision];
                                                      return (
                                                          <Paper 
                                                              key={revision} 
                                                              className={classes.releaseNoteRow}
                                                              elevation={1}
                                                          >
                                                              <div className={classes.releaseNoteHeader}>
                                                                  <Typography variant="subtitle1" style={{ fontWeight: 'bold' }}>
                                                                      Revision {revision}
                                                                  </Typography>
                                                                  <IconButton
                                                                      size="small"
                                                                      color="secondary"
                                                                      onClick={() => deleteReleaseNote(packageIndex, revision)}
                                                                  >
                                                                      <DeleteIcon />
                                                                  </IconButton>
                                                              </div>
                                                              
                                                              <TextField
                                                                  label="Date"
                                                                  type="date"
                                                                  variant="outlined"
                                                                  fullWidth
                                                                  className={classes.textField}
                                                                  value={releaseNote.date || ''}
                                                                  onChange={(e) => updateReleaseNote(packageIndex, revision, 'date', e.target.value)}
                                                                  InputLabelProps={{
                                                                      shrink: true,
                                                                  }}
                                                              />
                                                              
                                                              <TextField
                                                                  label="Description (Markdown supported)"
                                                                  variant="outlined"
                                                                  fullWidth
                                                                  multiline
                                                                  rows={4}
                                                                  className={classes.textField}
                                                                  value={releaseNote.description || ''}
                                                                  onChange={(e) => updateReleaseNote(packageIndex, revision, 'description', e.target.value)}
                                                                  placeholder="Enter release note description in Markdown format..."
                                                              />
                                                          </Paper>
                                                      );
                                                  })
                                              )}
                                          </div>
                                      </AccordionDetails>
                                  </Accordion>
                              ))}
                          </div>
                      )}

                      {packages.length === 0 && !loading && (
                          <Typography variant="body1" color="textSecondary" style={{ marginTop: '20px' }}>
                              Select a folder to load package summary files (_summary.json)
                          </Typography>
                      )}
                  </Paper>

                  {/* Add Release Note Dialog */}
                  <Dialog 
                      open={addReleaseNoteDialog.open} 
                      onClose={closeAddReleaseNoteDialog}
                      maxWidth="sm"
                      fullWidth
                  >
                      <DialogTitle>Add Release Note</DialogTitle>
                      <DialogContent>
                          <TextField
                              autoFocus
                              margin="dense"
                              label="Revision Key"
                              type="text"
                              fullWidth
                              variant="outlined"
                              value={addReleaseNoteDialog.revisionKey}
                              onChange={(e) => setAddReleaseNoteDialog({
                                  ...addReleaseNoteDialog,
                                  revisionKey: e.target.value
                              })}
                              helperText="Enter the revision number or key for this release note"
                              placeholder="e.g., 186, 187, or any custom key"
                          />
                      </DialogContent>
                      <DialogActions>
                          <Button onClick={closeAddReleaseNoteDialog} color="secondary">
                              Cancel
                          </Button>
                          <Button onClick={addReleaseNote} color="primary" variant="contained">
                              Add
                          </Button>
                      </DialogActions>
                  </Dialog>
              </div>
          </Container>
        </div>
    );
};

export default withStyles(useStyles)(ManageReleaseNotes);