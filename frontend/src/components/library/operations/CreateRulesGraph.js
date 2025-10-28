import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";
import { ForceGraph2D, ForceGraph3D } from "react-force-graph";
import FormGroup from "@material-ui/core/FormGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Checkbox from "@material-ui/core/Checkbox";
import SpriteText from "three-spritetext";
import { failedToast } from "../../utils/toastFunctions";

const useStyles = makeStyles((theme) => ({
    root: {
      display: 'flex',
    },
    container: {
      paddingTop: theme.spacing(4),
      paddingBottom: theme.spacing(4),
    },
}));

const CreateRulesGraph = (props) => {
    const classes = useStyles();
    const { version, library } = props;
    
    const [data, setData] = useState({"nodes":[], "links":[]});
    const [graph3d, setGraph3d] = useState(false);

    useEffect(() => {
        axios.get('/api/version/' + version + "/" + library + "/getRulesGraph")
            .then(res => {
                if(res.status === 200){
                    setData(res.data);
                }
            })
            .catch(err => failedToast(err));
    }, [version, library]);

    const handleChange = (event) => {
        setGraph3d(event.target.checked);
    };

    return (
        <div className={classes.root}>
          <CssBaseline />
          <Container maxWidth="lg" className={classes.container}>
              <div>
                  <Typography variant="h4">
                      Rules Graph
                  </Typography>
                  { graph3d &&
                    <ForceGraph3D graphData={data}
                                  width={1000}
                                  height={500}
                                  enablePointerInteraction={true}
                                  enableNodeDrag={true}
                                  nodeLabel="message"
                                  linkWidth={3}
                                  nodeId="id"
                                  nodeVal={10}
                                  nodeThreeObject={node => {
                                      const sprite = new SpriteText(node.message);
                                      sprite.color = node.color;
                                      sprite.textHeight = 8;
                                      return sprite;
                                  }}
                    />
                  }
                  { !graph3d &&
                  <ForceGraph2D graphData={data}
                                backgroundColor={"#e5e5e5"}
                                width={1000}
                                height={500}
                                enablePointerInteraction={true}
                                enableNodeDrag={true}
                                nodeLabel="message"
                                linkDirectionalArrowLength={10}
                                linkDirectionalArrowRelPos={1}
                                linkWidth={3}
                                nodeId="id"
                                nodeVal={10}
                                nodeCanvasObject={(node, ctx) => {
                                    const label = node.message;

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
                  }
                  <FormGroup row>
                      <FormControlLabel
                          control={<Checkbox checked={graph3d} onChange={handleChange} name="change-dim" />}
                          label="See in 3D"
                      />
                  </FormGroup>
              </div>
          </Container>
        </div>
    );
};

export default CreateRulesGraph;