import * as React from 'react';
import Popover from '@mui/material/Popover';
import Typography from '@mui/material/Typography';
import { styled } from '@mui/material/styles';
import { yellow } from '@mui/material/colors';
import Button from '@mui/material/Button';
import ShowMore from "./ShowMore"


const ColorButton = styled(Button)(({ theme }) => ({
    color: theme.palette.getContrastText(yellow[500]),
    backgroundColor: yellow[500],
    padding: 0,
    '&:hover': {
      backgroundColor: yellow[700],
    },
}));

export default function PopOver({text, externalText}) {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const [externalTextObj, setexternalTextObj] = React.useState({});
  const handleClick = (event) => {
    //Fix this if statement logic when there are target phrase and matching info from the api 
    Object.entries(externalText).forEach(([key, value]) => {
        if (key === text) alert("Not a valid target phrase")
        else {
            setexternalTextObj(externalText)
            //console.log("Invalid Target Phrase", externalTextObj)
        }
    })
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);
  const id = open ? 'simple-popover' : undefined;

  return (
    <span>
      <ColorButton aria-describedby={id} variant="contained" onClick={handleClick}>
        {text}
      </ColorButton>
      <Popover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
      >
        {(Object.keys(externalTextObj).length !== 0) ? 
        <Typography style={{width: 200, borderRadius: "2%", padding: "1%", textAlign:"Center"}}>
            <span style={{fontWeight: "bold"}}>{externalText.ExternalText.key}</span>
            <br/>
            <span style={{fontWeight: "bold"}}>Name of Standard:</span>
            <br/>
            <span style={{fontWeight: "bold"}}>Page Number: </span>{externalText.ExternalText.value.pageNumber}
            <br/>
            <span style={{fontWeight: "bold"}}>Score: </span>{externalText.ExternalText.value.score}
            <br/>
            <ShowMore externalText={externalText}/>
        
        </Typography> : null
        /* <Typography style={{width: 200, borderRadius: "2%", padding: "1%", textAlign:"Center"}}>
            <span style={{fontWeight: "bold"}}>Not Valid Target Phrase</span>
        </Typography>  */
        }
      </Popover>
    </span>
  );
}