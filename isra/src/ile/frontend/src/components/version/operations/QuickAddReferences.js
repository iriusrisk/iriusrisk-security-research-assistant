import React, {useState} from 'react';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import {easyToast, failedToast} from "../../utils/toastFunctions";
import Grid from "@material-ui/core/Grid";
import TextField from "@material-ui/core/TextField";
import Button from "@material-ui/core/Button";

const QuickAddReferences = ({version, update}) => {
    const [name, setName] = useState("");
    const [url, setUrl] = useState("");

    const addReference = () => {
        if(name !== "" && url !== ""){
            let reference = {
                name: name,
                url: url
            };
            axios.post('/version/'+version+'/reference', reference)
                .then(res => {
                    easyToast(res, "Reference added", "Reference couldn't be added");
                    if(res.status === 200){
                        update();
                    }
                })
                .catch(err => failedToast("Reference couldn't be added: "+err));
        }else{
            failedToast("Empty name or URL");
        }
    };

    const handleName = (event) => {
        setName(event.target.value);
    };

    const handleUrl = (event) => {
        setUrl(event.target.value);
    };

    return(
        <div>
            <Typography variant="body1">
                Create new reference
            </Typography>
            <Grid container>
                <Grid item xs={4}>
                    <TextField
                        variant="outlined"
                        margin="normal"
                        fullWidth
                        id="refname"
                        label="Reference name"
                        defaultValue=""
                        onChange={handleName}
                    />
                </Grid>
                <Grid item xs={4}>
                    <TextField
                        variant="outlined"
                        margin="normal"
                        fullWidth
                        id="refurl"
                        label="Reference url"
                        defaultValue=""
                        onChange={handleUrl}
                    />
                </Grid>
                <Grid item xs={4}>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={addReference}
                    >
                        Create
                    </Button>
                </Grid>
            </Grid>
        </div>
    );
};

export default QuickAddReferences;