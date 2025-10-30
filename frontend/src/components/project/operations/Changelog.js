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
import ReactHtmlParser from 'react-html-parser';

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
    }
});

const Changelog = (props) => {
    const { classes, data: propsData, noGraph: propsNoGraph } = props;
    const [data, setData] = useState(propsData);
    const [elements, setElements] = useState({});
    const [noGraph] = useState(propsNoGraph !== undefined ? propsNoGraph : false);
    const [selectedNode, setSelectedNode] = useState("");

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
          <div>

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
                      <Grid container spacing={3}>
                          <Grid item xs={12}>
                              <Typography>
                                  Selected node: {selectedNode.name}
                              </Typography>
                          </Grid>
                          {selectedNode.changes.map((value2,index2) => {
                              return [
                                  <Grid key={index2} item xs={4}>
                                      <Typography style={{ fontWeight: 600 }}>
                                          {value2.field}
                                      </Typography>
                                  </Grid>,
                                  <Grid key={index2 + 10000} item xs={4}>
                                      { ReactHtmlParser (value2.old) }
                                  </Grid>,
                                  <Grid key={index2 + 1000000} item xs={4}>
                                      { ReactHtmlParser (value2.neww) }
                                  </Grid>
                              ]
                          })}
                      </Grid>

                    }

                </Grid>
            </div>

          }
          { data.changelogList.length !== 0 &&
            <Paper>
                <Typography variant="h5">
                    Changelog
                </Typography>

                {
                    Object.keys(elements).map(function(keyName, keyIndex) {
                        let elem = elements[keyName];
                        return <Accordion key={keyIndex} expanded={true}>
                            <AccordionSummary
                                aria-controls="panel1a-content"
                                id="panel1a-header"
                            >
                                <Typography variant="h6">{keyName}</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                                <List>
                                    {elem.map((value, index) => {
                                        let color = undefined;
                                        switch (value.action) {
                                            case "E":
                                                color = classes.editedItem;
                                                break;
                                            case "N":
                                                color = classes.newItem;
                                                break;
                                            case "D":
                                                color = classes.deletedItem;
                                                break;
                                            default:
                                                break;
                                        }

                                        return <ListItem key={index} className={color}>
                                            <Grid container spacing={3}>
                                                <Grid item xs={12}>
                                                    <Typography>
                                                        {value.info}
                                                    </Typography>
                                                </Grid>
                                                {value.changes.map((value2,index2) => {
                                                    return [
                                                        <Grid key={index2} item xs={4}>
                                                            <Typography style={{ fontWeight: 600 }}>
                                                                {value2.field}
                                                            </Typography>
                                                        </Grid>,
                                                        <Grid key={index2 + 10000} item xs={4}>
                                                            { ReactHtmlParser (value2.old) }
                                                        </Grid>,
                                                        <Grid key={index2 + 1000000} item xs={4}>
                                                            { ReactHtmlParser (value2.neww) }
                                                        </Grid>
                                                    ]
                                                })}
                                            </Grid>
                                        </ListItem>
                                    })}
                                </List>
                            </AccordionDetails>
                        </Accordion>
                    })
                }

            </Paper>

          }
          </div>
        </div>
    );
};

export default withStyles(useStyles)(Changelog);