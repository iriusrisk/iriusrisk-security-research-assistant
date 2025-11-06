import React, { useState, useEffect } from 'react';
import { withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Typography from "@material-ui/core/Typography";
import { ForceGraph2D } from 'react-force-graph';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import Grid from "@material-ui/core/Grid";
import Paper from "@material-ui/core/Paper";
import Chip from '@material-ui/core/Chip';
import Box from '@material-ui/core/Box';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import ReactHtmlParser from 'react-html-parser';

const useStyles = (theme) => ({
    root: {
      display: 'flex'
    },
    container: {
      paddingTop: theme.spacing(4),
      paddingBottom: theme.spacing(4)
    },
    changelogPaper: {
        padding: theme.spacing(3),
        marginTop: theme.spacing(2)
    },
    changeItem: {
        marginBottom: theme.spacing(2),
        borderRadius: theme.shape.borderRadius,
        transition: 'all 0.2s ease-in-out',
    },
    oldValuePaper: {
        padding: theme.spacing(1.5),
        backgroundColor: '#fff5f5',
        borderLeft: '3px solid #f97678',
        borderRadius: theme.shape.borderRadius,
    },
    newValuePaper: {
        padding: theme.spacing(1.5),
        backgroundColor: '#f0fff4',
        borderLeft: '3px solid #13e29d',
        borderRadius: theme.shape.borderRadius,
    },
    fieldLabel: {
        fontWeight: 600,
        marginBottom: theme.spacing(1),
        color: theme.palette.text.secondary,
    },
    valueLabel: {
        fontWeight: 600,
        textTransform: 'uppercase',
        fontSize: '0.7rem',
        marginBottom: theme.spacing(0.5),
    },
    emptyValue: {
        fontStyle: 'italic',
        color: theme.palette.text.disabled,
    }
});

const Changelog = (props) => {
    const { classes, data: propsData, noGraph: propsNoGraph } = props;
    const [data, setData] = useState(propsData);
    const [elements, setElements] = useState({});
    const [noGraph] = useState(propsNoGraph !== undefined ? propsNoGraph : false);
    const [selectedNode, setSelectedNode] = useState("");
    const [expandedSections, setExpandedSections] = useState({});

    // Helper functions
    const getColorHex = (action) => {
        switch (action) {
            case "E": return "#ffe381";
            case "N": return "#13e29d";
            case "D": return "#f97678";
            default: return "#cdf0ff";
        }
    };

    const getActionLabel = (action) => {
        switch (action) {
            case "E": return "EDITED";
            case "N": return "NEW";
            case "D": return "DELETED";
            default: return "UNKNOWN";
        }
    };

    const renderValue = (htmlContent) => {
        if (!htmlContent || htmlContent.trim() === '' || htmlContent === 'null' || htmlContent === 'undefined') {
            return <span className={classes.emptyValue}>No value</span>;
        }
        return ReactHtmlParser(htmlContent);
    };

    useEffect(() => {
        let newElements = {};
        data.changelogList.forEach(x => {
            if(newElements[x.element] === undefined) {
                newElements[x.element] = [];
            }
            newElements[x.element].push(x);
        });

        setElements(newElements);
    }, [data]);

    useEffect(() => {
        if(propsData !== data){
            let newElements = {};
            propsData.changelogList.forEach(x => {
                if(newElements[x.element] === undefined) {
                    newElements[x.element] = [];
                }
                newElements[x.element].push(x);
            });

            setData(propsData);
            setElements(newElements);
        }
    }, [propsData, data]);

    const onClickNode = (node, event) => {
        setSelectedNode(node);
    };

    return (
        <div className={classes.root}>
          <CssBaseline />
          <div style={{width: '100%'}}>

          { noGraph === false && data.nodes.length !== 0 && data.links.length !== 0 &&

            <div>
                <Grid container>
                    <Grid item xs={12}>
                        <ForceGraph2D graphData={data}
                                      backgroundColor={"#e5e5e5"}
                                      width={1000}
                                      height={500}
                                      enablePointerInteraction={true}
                                      enableNodeDrag={true}
                                      nodeLabel="name"
                                      onNodeClick={onClickNode}
                                      linkWidth={3}
                                      nodeId="id"
                                      nodeVal={10}
                                      nodeCanvasObject={(node, ctx) => {
                                          const label = node.name;

                                          ctx.beginPath();
                                          ctx.lineWidth = 1;
                                          ctx.strokeStyle = node.color;
                                          ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
                                          ctx.fillStyle = node.color;
                                          ctx.fill();
                                          ctx.stroke();
                                          ctx.closePath();

                                          ctx.beginPath();
                                          ctx.fillStyle = "#000000";
                                          ctx.fillText(label, node.x + 9, node.y + 2);
                                          ctx.closePath();
                                      }}
                        />
                    </Grid>
                    { selectedNode !== "" &&
                      <Grid container spacing={3} style={{ marginTop: 16 }}>
                          <Grid item xs={12}>
                              <Paper elevation={2} style={{ padding: 16 }}>
                                  <Typography variant="h6" style={{ marginBottom: 16 }}>
                                      Selected node: {selectedNode.name}
                                  </Typography>
                                  {selectedNode.changes && selectedNode.changes.map((value2, index2) => (
                                      <Grid key={index2} container spacing={2} style={{ marginBottom: 16 }}>
                                          <Grid item xs={12}>
                                              <Typography className={classes.fieldLabel}>
                                                  {value2.field}
                                              </Typography>
                                          </Grid>
                                          <Grid item xs={6}>
                                              <Paper className={classes.oldValuePaper} elevation={0}>
                                                  <Typography className={classes.valueLabel} style={{ color: '#c53030' }}>
                                                      Old Value
                                                  </Typography>
                                                  <Typography variant="body2">
                                                      {renderValue(value2.old)}
                                                  </Typography>
                                              </Paper>
                                          </Grid>
                                          <Grid item xs={6}>
                                              <Paper className={classes.newValuePaper} elevation={0}>
                                                  <Typography className={classes.valueLabel} style={{ color: '#22543d' }}>
                                                      New Value
                                                  </Typography>
                                                  <Typography variant="body2">
                                                      {renderValue(value2.new)}
                                                  </Typography>
                                              </Paper>
                                          </Grid>
                                      </Grid>
                                  ))}
                              </Paper>
                          </Grid>
                      </Grid>
                    }

                </Grid>
            </div>

          }
          { data.changelogList.length !== 0 &&
            <Paper className={classes.changelogPaper} elevation={3}>
                <Typography variant="h5" style={{ marginBottom: 16 }}>
                    Changelog
                </Typography>

                {
                    Object.keys(elements).map(function(keyName, keyIndex) {
                        let elem = elements[keyName];
                        const isExpanded = expandedSections[keyName] !== false;
                        return (
                            <Accordion 
                                key={keyIndex} 
                                expanded={isExpanded}
                                onChange={() => setExpandedSections(prev => ({
                                    ...prev,
                                    [keyName]: !prev[keyName]
                                }))}
                                style={{ marginBottom: 8 }}
                            >
                                <AccordionSummary
                                    expandIcon={<ExpandMoreIcon />}
                                    aria-controls={`panel-${keyIndex}-content`}
                                    id={`panel-${keyIndex}-header`}
                                >
                                    <Box display="flex" alignItems="center" width="100%">
                                        <Typography variant="h6" style={{ flexGrow: 1 }}>
                                            {keyName}
                                        </Typography>
                                        <Chip 
                                            label={`${elem.length} change${elem.length !== 1 ? 's' : ''}`}
                                            size="small"
                                            style={{ marginRight: 16 }}
                                        />
                                    </Box>
                                </AccordionSummary>
                                <AccordionDetails>
                                    <List style={{ width: '100%' }}>
                                        {elem.map((value, index) => {
                                            const colorHex = getColorHex(value.action);
                                            const actionLabel = getActionLabel(value.action);

                                            return (
                                                <ListItem 
                                                    key={index} 
                                                    className={classes.changeItem}
                                                    style={{ 
                                                        backgroundColor: `${colorHex}20`,
                                                        borderLeft: `4px solid ${colorHex}`,
                                                        padding: 16,
                                                        marginBottom: 8,
                                                        display: 'block'
                                                    }}
                                                >
                                                    <Box display="flex" alignItems="center" justifyContent="space-between" style={{ marginBottom: 12 }}>
                                                        <Typography variant="subtitle1" style={{ fontWeight: 600 }}>
                                                            {value.info}
                                                        </Typography>
                                                        <Chip 
                                                            label={actionLabel}
                                                            size="small"
                                                            style={{ 
                                                                backgroundColor: colorHex,
                                                                color: 'white',
                                                                fontWeight: 600
                                                            }}
                                                        />
                                                    </Box>
                                                    {value.changes && value.changes.map((value2, index2) => (
                                                        <Paper 
                                                            key={index2} 
                                                            elevation={1} 
                                                            style={{ 
                                                                padding: 12, 
                                                                marginBottom: 12,
                                                                backgroundColor: 'white'
                                                            }}
                                                        >
                                                            <Typography className={classes.fieldLabel}>
                                                                {value2.field}
                                                            </Typography>
                                                            <Grid container spacing={2}>
                                                                <Grid item xs={6}>
                                                                    <Paper className={classes.oldValuePaper} elevation={0}>
                                                                        <Typography className={classes.valueLabel} style={{ color: '#c53030' }}>
                                                                            Old Value
                                                                        </Typography>
                                                                        <Typography variant="body2" style={{ marginTop: 4 }}>
                                                                            {renderValue(value2.old)}
                                                                        </Typography>
                                                                    </Paper>
                                                                </Grid>
                                                                <Grid item xs={6}>
                                                                    <Paper className={classes.newValuePaper} elevation={0}>
                                                                        <Typography className={classes.valueLabel} style={{ color: '#22543d' }}>
                                                                            New Value
                                                                        </Typography>
                                                                        <Typography variant="body2" style={{ marginTop: 4 }}>
                                                                            {renderValue(value2.new)}
                                                                        </Typography>
                                                                    </Paper>
                                                                </Grid>
                                                            </Grid>
                                                        </Paper>
                                                    ))}
                                                </ListItem>
                                            );
                                        })}
                                    </List>
                                </AccordionDetails>
                            </Accordion>
                        );
                    })
                }

            </Paper>

          }
          </div>
        </div>
    );
};

export default withStyles(useStyles)(Changelog);