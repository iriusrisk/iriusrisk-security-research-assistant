import React, {Component} from 'react';
import {withStyles} from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import axios from "axios";

const useStyles = (theme) => ({
    root: {
      display: 'flex',
    },
    container: {
      paddingTop: theme.spacing(4),
      paddingBottom: theme.spacing(4),
    },
});

class Template extends Component{
    constructor(props){
        super(props);
    };

    render(){
        const { classes } = this.props;

        return(
            <div className={classes.root}>
              <CssBaseline />
              <Container maxWidth="lg" className={classes.container}>
                  <Typography variant="h4">
                      Template
                  </Typography>

              </Container>
            </div>
        );
    }
}

export default withStyles(useStyles)(Template);