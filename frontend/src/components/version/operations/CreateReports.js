import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import Button from "@material-ui/core/Button";
import StatisticsReport from "./reports/StatisticsReport";
import ComponentsReport from "./reports/ComponentsReport";
import { failedToast } from "../../utils/toastFunctions";
import { sortStringArrayInsensitiveCase } from "../../utils/commonFunctions";
import ReactToPrint from "react-to-print";
import Select from "@material-ui/core/Select";

const useStyles = makeStyles((theme) => ({
    root: {
      display: 'flex',
    },
    container: {
      paddingTop: theme.spacing(4),
      paddingBottom: theme.spacing(4),
    },
    selected: {
        "&:hover": {
            backgroundColor: "#f97678",
        },
        backgroundColor: "#60d460"
    },
    notSelected: {
        "&:hover": {
            backgroundColor: "#13e29d",
        },
    }
}));

const CreateReports = (props) => {
    const classes = useStyles();
    const { version } = props;
    
    const [activeReport, setActiveReport] = useState("");
    const [selectedReport, setSelectedReport] = useState("componentsReport");
    const [availableLibraries, setAvailableLibraries] = useState([]);
    const [selectedLibraries, setSelectedLibraries] = useState([]);
    
    const availableReports = {
        "componentsReport": "the components ordered by category",
        "statisticsReport": "the number of use cases, threats, weaknesses and controls for each risk pattern"
    };

    useEffect(() => {
        axios.get('/version/' + version + "/report")
            .then(res => {
                let av = [];
                res.data.libraryReport.forEach(value => {
                    if (value.libraryRef === "all-libraries") {
                        failedToast("There is a library called 'all-libraries'. This may produce conflicts");
                    }
                    av.push(value.libraryRef);
                    sortStringArrayInsensitiveCase(av);
                });
                setAvailableLibraries(av);
                setSelectedLibraries(Array.from(av));
            })
            .catch(err => failedToast(err));
    }, [version]);

    const handleReportType = (report) => {
        setSelectedReport(report);
    };

    const handleSubmit = (event) => {
        if (selectedLibraries.length === 0) {
            failedToast("Select at least one library");
        } else {
            setActiveReport(selectedReport);
        }
        event.preventDefault();
    };

    const back = () => {
        setActiveReport("");
    };

    const selectLibrary = (lib) => {
        if (lib === "all-libraries") {
            setSelectedLibraries(sortStringArrayInsensitiveCase(Array.from(availableLibraries)));
        } else {
            let n = [...selectedLibraries];
            n.push(lib);
            sortStringArrayInsensitiveCase(n);
            setSelectedLibraries(n);
        }
    };

    const deselectLibrary = (lib) => {
        if (lib === "all-libraries") {
            setSelectedLibraries([]);
        } else {
            const index = selectedLibraries.indexOf(lib);
            if (index > -1) {
                let n = [...selectedLibraries];
                n.splice(index, 1);
                setSelectedLibraries(n);
            }
        }
    };

    return (
        <div className={classes.root}>
            <CssBaseline />
            <Container maxWidth="lg" className={classes.container}>
                <Typography variant="h4">
                    Create Reports
                </Typography>
                {activeReport === "" &&
                    <div>
                        <div>
                            <Typography variant="h6">
                                I want a report about...
                            </Typography>
                            <Select
                                native
                                value={selectedReport}
                                variant="outlined"
                                onChange={(event) => handleReportType(event.target.value)}
                            >
                                {Object.keys(availableReports).map((value, index) => {
                                    return <option key={index} value={value}>{availableReports[value]}</option>
                                })}
                            </Select>
                        </div>
                        <div>
                            <Typography variant="h6">
                                From the libraries...
                            </Typography>
                        </div>
                        <div>
                            {availableLibraries.map((value, index) => {
                                if (selectedLibraries.includes(value)) {
                                    return <Button key={index} className={classes.selected} variant="contained" onClick={() => deselectLibrary(value)}>{value}</Button>
                                } else {
                                    return <Button key={index} className={classes.notSelected} variant="contained" onClick={() => selectLibrary(value)}>{value}</Button>
                                }
                            })}
                        </div>
                        <br />
                        <div>
                            <Button variant="contained" onClick={() => selectLibrary("all-libraries")}>Select all</Button>
                            <Button variant="contained" onClick={() => deselectLibrary("all-libraries")}>Deselect all</Button>
                        </div>
                        <div>
                            <Button variant="contained" color="primary" onClick={handleSubmit}>Submit</Button>
                        </div>
                    </div>
                }

                {activeReport !== "" &&
                    <ReactToPrint
                        trigger={() => { return <Button variant="contained" color="primary">Export PDF</Button>; }}
                        content={() => document.getElementById('print-content')}
                    />
                }

                <div id="print-content">
                    {activeReport === "statisticsReport" &&
                        <StatisticsReport version={version} libraries={selectedLibraries} back={back} />
                    }

                    {activeReport === "componentsReport" &&
                        <ComponentsReport version={version} libraries={selectedLibraries} back={back} />
                    }
                    
                </div>

            </Container>
        </div>
    );
};

export default CreateReports;