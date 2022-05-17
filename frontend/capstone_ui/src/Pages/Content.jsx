import * as React from 'react';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import DocumentView from './DocumentView';
import { useState } from 'react';
import TextView from './TextView';
import FetchTargetPhrase from './FetchTargetPhrase'
export default function Content() {
/*
Description: This is a main page where upload functionality will be implemented. The 'Document View' and 'Text View' buttons will be replaced with 'Submit' button
*/

  //Change state and load up component once 'Submit' button is clicked
  const [document, setDocument] = useState(false);
  const [text, setText] = useState(false);
  const onSubmitDocument=()=>{
    setDocument(true)
  }
  const onSubmitText=()=>{
    setText(true)
  }
  return (
    <Paper sx={{ maxWidth: 936, margin: 'auto', overflow: 'hidden' }}>

     {document === true? <DocumentView/> : 
      <Button
          onClick={onSubmitDocument}
      >
      Document View
      </Button>
    }
     
    {text === true? <TextView/> : 
      <Button
          onClick={onSubmitText}
      >
      Text View
      </Button>
    }
    {/* <FetchTargetPhrase/> */}
    </Paper>
  );
}