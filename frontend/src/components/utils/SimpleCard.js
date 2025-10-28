import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import {Link} from "react-router-dom";
import DeleteIcon from '@material-ui/icons/Delete';
import GetAppIcon from '@material-ui/icons/GetApp';
import PlusOneIcon from '@material-ui/icons/PlusOne';
import IconButton from "@material-ui/core/IconButton";
import Tooltip from "@material-ui/core/Tooltip";
import CardActionArea from "@material-ui/core/CardActionArea";

const useStyles = makeStyles({
     root: {
         backgroundColor: "#e2eeff",
         "&:hover": {
             backgroundColor: "#c0daff",
         },
         "&:active": {
             backgroundColor: "#91caff",
         },
     },
     rootGreen: {
         backgroundColor: "#b7f9b2",
         "&:hover": {
             backgroundColor: "#13e29d",
         },
         "&:active": {
             backgroundColor: "#16cb48",
         },
     },
     rootRed: {
         backgroundColor: "#f97678",
         "&:hover": {
             backgroundColor: "#ff574d",
         },
         "&:active": {
             backgroundColor: "#d94843",
         },
     },
     rootYellow: {
         backgroundColor: "#f9f9bf",
         "&:hover": {
             backgroundColor: "#f5ffa3",
         },
         "&:active": {
             backgroundColor: "#fff77c",
         },
     },
     pos: {
         marginBottom: 12,
     },
     noDec: {
         textDecoration: "none"
     },
     iconButtons:{
         "&.MuiIconButton-root": {
             padding: 0
         }
     },
    cardRoot:{
        "&.MuiCardContent-root": {
            paddingBottom: "24px"
        }
    }

 });

const renderCardContent = (props, classes) => {
    return <CardContent className={classes.cardRoot}>
         <Typography variant="h5">
             {props.title}
         </Typography>
        <Typography component={'span'} className={classes.pos} color="textSecondary">
            <div>
                {props.subtitle != null && <div>{props.subtitle}</div>}
                {props.subtitle2 != null && <div>{props.subtitle2}</div>}
                {props.subtitle3 != null && <div>{props.subtitle3}</div>}
                {props.subtitle4 != null && <div>{props.subtitle4}</div>}
                {props.subtitle5 != null && <div>{props.subtitle5}</div>}
            </div>
        </Typography>


    </CardContent>
};

export default function SimpleCard(props) {
    const classes = useStyles();

    let classColor;
    switch (props.color) {
        case "green":
            classColor = classes.rootGreen;
            break;
        case "red":
            classColor = classes.rootRed;
            break;
        case "yellow":
            classColor = classes.rootYellow;
            break;
        default:
            classColor = classes.root;
    }

    if(props.link !== undefined){
        return (
            <Card className={classColor} elevation={3}>
                <CardActionArea component={Link} to={props.link}>
                    {renderCardContent(props, classes)}
                </CardActionArea>
                {props.delete !== undefined &&
                 <IconButton className={classes.iconButtons} color="primary" component="span" onClick={()=>props.delete(props)}>
                     <DeleteIcon />
                 </IconButton>
                }

                {props.download !== undefined &&
                 <Tooltip title="XML" placement="top-end">
                     <IconButton className={classes.iconButtons} color="primary" component="span" onClick={()=>props.download(props)}>
                         <GetAppIcon />
                     </IconButton>
                 </Tooltip>
                }

                {props.revision !== undefined &&
                 <IconButton className={classes.iconButtons} color="primary" component="span" onClick={()=>props.revision(props)}>
                     <PlusOneIcon />
                 </IconButton>
                }
            </Card>
        );
    }

    return (
        <Card className={classColor} elevation={3}>
            {renderCardContent(props, classes)}
        </Card>
    );
}