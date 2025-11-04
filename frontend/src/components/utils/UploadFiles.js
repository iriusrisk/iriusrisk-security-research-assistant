import React, {Component} from "react";
import LinearProgress from '@material-ui/core/LinearProgress';
import {Box, Button, Typography, withStyles, List, ListItem, ListItemText, ListItemIcon, Paper, Chip} from '@material-ui/core';
import UploadService from "./UploadService";
import {successToast, failedToast} from "./toastFunctions";
import InsertDriveFileIcon from '@material-ui/icons/InsertDriveFile';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import DeleteIcon from '@material-ui/icons/Delete';

const BorderLinearProgress = withStyles((theme) => ({
    root: {
        height: 15,
        borderRadius: 5,
    },
    colorPrimary: {
        backgroundColor: "#EEEEEE",
    },
    bar: {
        borderRadius: 5,
        backgroundColor: '#1a90ff',
    },
}))(LinearProgress);

export default class UploadFiles extends Component {
    constructor(props) {
        super(props);
        this.version = props.version;
        this.selectFile = this.selectFile.bind(this);
        this.upload = this.upload.bind(this);
        this.removeFile = this.removeFile.bind(this);

        this.state = {
            selectedFiles: [],
            currentFile: undefined,
            progress: 0,
            message: "",
            isError: false,
            isUploading: false
        };
    }

    componentDidMount() {

    }

    selectFile(event) {
        const newFiles = Array.from(event.target.files);
        this.setState({
          selectedFiles: [...this.state.selectedFiles, ...newFiles],
        });
    }

    removeFile(index) {
        const updatedFiles = this.state.selectedFiles.filter((_, i) => i !== index);
        this.setState({
            selectedFiles: updatedFiles
        });
    }

    upload() {
        let currentFiles = this.state.selectedFiles;

        if (currentFiles.length === 0) {
            failedToast("Please select files to upload!");
            return;
        }

        this.setState({
          progress: 0,
          isUploading: true
        });

        UploadService.upload(currentFiles, this.version, (event) => {
            this.setState({
              progress: Math.round((100 * event.loaded) / event.total),
            });
        })
            .then((response) => {
                this.setState({
                  message: response.data.message,
                  isError: false,
                  isUploading: false
                });
            })
            .then(() => {
                successToast("Files imported successfully");
                this.setState({
                    selectedFiles: []
                });
            })
            .catch(() => {
                failedToast("Could not upload the files!");
                this.setState({
                  progress: 0,
                  message: "Could not upload the files!",
                  currentFile: undefined,
                  isError: true,
                  isUploading: false
                });
            });
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    render() {
        const {
            selectedFiles,
            currentFile,
            progress,
            message,
            isError,
            isUploading
        } = this.state;

        return (
            <Box>
                {currentFile && (
                    <Box className="mb25" display="flex" alignItems="center">
                        <Box width="100%" mr={1}>
                            <BorderLinearProgress variant="determinate" value={progress} />
                        </Box>
                        <Box minWidth={35}>
                            <Typography variant="body2" color="textSecondary">{`${progress}%`}</Typography>
                        </Box>
                    </Box>)
                }

                {/* File Selection */}
                <Box mb={3}>
                    <label htmlFor="btn-upload">
                        <input
                            id="btn-upload"
                            name="btn-upload"
                            style={{ display: 'none' }}
                            type="file"
                            accept=".xml,.xlsx,.xls,.yaml"
                            multiple={true}
                            onChange={this.selectFile} />
                        <Button
                            variant="outlined"
                            component="span"
                            startIcon={<CloudUploadIcon />}
                            disabled={isUploading}
                            style={{ marginBottom: '16px' }}>
                            Choose Library Files
                        </Button>
                    </label>
                </Box>

                {/* File Preview List */}
                {selectedFiles && selectedFiles.length > 0 && (
                    <Paper elevation={1} style={{ marginBottom: '24px', maxHeight: '300px', overflow: 'auto' }}>
                        <Box p={2}>
                            <Typography variant="h6" gutterBottom>
                                Selected Files ({selectedFiles.length})
                            </Typography>
                            <List dense>
                                {Array.from(selectedFiles).map((file, index) => (
                                    <ListItem key={index} divider={index < selectedFiles.length - 1}>
                                        <ListItemIcon>
                                            <InsertDriveFileIcon color="primary" />
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={file.name}
                                            secondary={`${this.formatFileSize(file.size)} • ${file.type || 'Unknown type'}`}
                                        />
                                        <Button
                                            size="small"
                                            color="secondary"
                                            onClick={() => this.removeFile(index)}
                                            disabled={isUploading}
                                            startIcon={<DeleteIcon />}
                                        >
                                            Remove
                                        </Button>
                                    </ListItem>
                                ))}
                            </List>
                        </Box>
                    </Paper>
                )}

                {/* Upload Button */}
                <Box display="flex" alignItems="center" gap={2}>
                    <Button
                        color="primary"
                        variant="contained"
                        component="span"
                        disabled={!selectedFiles || selectedFiles.length === 0 || isUploading}
                        onClick={this.upload}
                        startIcon={<CloudUploadIcon />}
                        style={{ 
                            padding: '12px 24px',
                            borderRadius: '8px',
                            textTransform: 'none',
                            fontWeight: 600
                        }}>
                        {isUploading ? 'Uploading...' : `Upload ${selectedFiles.length} File${selectedFiles.length !== 1 ? 's' : ''}`}
                    </Button>
                    
                    {selectedFiles.length > 0 && (
                        <Chip 
                            label={`${selectedFiles.length} file${selectedFiles.length !== 1 ? 's' : ''} selected`}
                            color="primary"
                            variant="outlined"
                        />
                    )}
                </Box>

                {/* Status Message */}
                {message && (
                    <Typography 
                        variant="body2" 
                        style={{ 
                            marginTop: '16px',
                            color: isError ? '#f44336' : '#4caf50',
                            fontWeight: isError ? 600 : 400
                        }}
                    >
                        {message}
                    </Typography>
                )}
            </Box>
        );
    }
}