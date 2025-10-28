import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import Button from "@material-ui/core/Button";
import { sortArrayByKey } from "../../../utils/commonFunctions";
import { failedToast } from "../../../utils/toastFunctions";

const useStyles = makeStyles((theme) => ({
    root: {
      display: 'flex',
    },
    container: {
      paddingTop: theme.spacing(4),
      paddingBottom: theme.spacing(4),
    },
}));

const ComponentsReport = (props) => {
    const classes = useStyles();
    const { version, libraries, back } = props;
    
    const [items, setItems] = useState([]);

    useEffect(() => {
        axios.get('/version/' + version)
            .then(res => {
                let fullVersion = res.data;
                let its = [];

                const categoryNames = new Map();
                for (const [catKey, catValue] of Object.entries(fullVersion.categories)) {
                    categoryNames.set(catKey, catValue.name);
                }

                for (const [libKey, libValue] of Object.entries(fullVersion.libraries)) {
                    if (libraries.includes(libKey)) {
                        const categoryMap = new Map();

                        Object.values(libValue.componentDefinitions).forEach(comp => {
                            let categoryName = categoryNames.get(comp.categoryRef);
                            if (categoryMap.has(categoryName)) {
                                categoryMap.get(categoryName).push(comp.name);
                            } else {
                                categoryMap.set(categoryName, []);
                                categoryMap.get(categoryName).push(comp.name);
                            }
                        });

                        its.push({ lib: libValue.name, vers: libValue.revision, cat: Array.from(categoryMap) });
                        sortArrayByKey(its, "lib")
                    }
                }

                setItems(its);
            })
            .catch(err => failedToast(err));
    }, [version, libraries]);

    return (
        <div className={classes.root}>
            <CssBaseline />
            <Container maxWidth="lg" className={classes.container}>
                <Typography variant="h4">
                    Components Report
                </Typography>
                <div>
                    <Button variant="contained" color="primary" onClick={back}>Back</Button>
                    <div>Version: {version}</div>
                    {items.map((value, index) => {
                        return [
                            <h2 key={"h" + index}>Library name: {value.lib} [Library Version: {value.vers}]</h2>,
                            <ul key={"ul" + index}>
                                {Object.keys(value.cat).map((value2, index2) => {
                                    return [
                                        <li key={"li" + index2}>Category Name: {value.cat[value2][0]}</li>,
                                        <ul key={"ul2" + index2}>
                                            {value.cat[value2][1].map((v, index3) => {
                                                return <li key={"lii" + index3}>{v}</li>;
                                            })}
                                        </ul>]
                                })}
                            </ul>]
                    })}
                </div>
            </Container>
        </div>
    );
};

export default ComponentsReport;