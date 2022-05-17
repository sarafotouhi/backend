import React from "react";
import Highlighter from "react-highlight-words";
import PopOver from "./PopOver";
/*
Description: This class will call the API that fetches target phrases from AWS server && iterate through the contract text array and displays its content
*/
class DisplayText extends React.Component {
    // Constructor
	constructor(props) {
		super(props);

		this.state = {
			targetPhraseData: null,
            renderAgain: false,
            TextDoc: "",
            ExternalTextObj: {}
		};

        this.getTargetPhrase = this.getTargetPhrase.bind(this);
        this.updateTargetPhraseData = this.updateTargetPhraseData.bind(this);
        this.generateTextString = this.generateTextString.bind(this);
	}

    updateTargetPhraseData (data){
		this.setState({targetPhraseData: data});
		console.log(this.state.targetPhraseData);
	}

    async getTargetPhrase(requestOptions) {
        let response = await fetch('http://cs4470capstone-env.eba-f9wabacx.us-east-1.elasticbeanstalk.com/requirements', requestOptions)
        let data = await response.json()
        console.log(data);
        this.updateTargetPhraseData(data);
        return data;
    }

    generateTextString(){
        let tempPage = "";
       //In this function we can manupulate contract doc text to check for newline and add \n when line ends
        this.props.TextArray.map((Page) => 
            tempPage += Page.map((line)=>  (line.str === '\r\n') ? `${line.str} \n` : `${line.str}`).join(' ')
        
        // {
        //     console.log(Page)
        //     return tempPage += Page.map((line)=>  (line.str === '\r\n') ? `${line.str} \n` : `${line.str}`).join(' ')
        // }
           
        ) 
        console.log("TempPage", tempPage);
        this.setState({TextDoc: tempPage});
        console.log(this.state.TextDoc);
    }
    
    updateExternalTextObj(ExtTextObj){
		this.setState({ExternalTextObj: ExtTextObj});
		console.log(this.state.ExternalTextObj);
	}   

    async getExternalText(requestExternalText) {
        let response = await fetch('http://cs4470capstone-env.eba-f9wabacx.us-east-1.elasticbeanstalk.com/requirements', requestExternalText)
        let data = await response.json()
        console.log(data);
        this.updateExternalTextObj(data);
        return data;
    }

    componentDidMount() {
        const requestTargetPhrases = {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"
            },
            body: JSON.stringify({ title: 'Target Phrase' })
        };

        this.getTargetPhrase(requestTargetPhrases);
        console.log(this.state.targetPhraseData);
        this.generateTextString();

        const requestExternalText = {
            method: 'GET',
            headers: { 
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"
            },
            // body: JSON.stringify({ title: 'Target Phrase' })
        };
		this.getExternalText(requestExternalText);
        console.log(this.state.targetPhraseData);
        this.setState({renderAgain: true});
		
	}
    
	
	render() {
        let Highlight;
		if (!this.state.renderAgain) 
			return <div>Fetching Contract ...</div> 

        if (Object.keys(this.state.ExternalTextObj).length !== 0){
            Highlight = ({ children, highlightIndex }) => (
                <PopOver
                    className="highlighted-text" 
                    style={{backgroundColor: "Yellow"}} 
                    text={children} 
                    externalText={this.state.ExternalTextObj}
                />
               
                //Use this code to show pop when button is clicked
                // Object.entries(this.state.ExternalTextObj).forEach(([key, value]) => {
                //     if (key === children) 
                //         return (
                //         <PopUp 
                //             className="highlighted-text" 
                //             style={{backgroundColor: "Yellow"}} 
                //             text={children} 
                //             externalText={this.state.ExternalTextObj}
                //         />
                //         )
                // })
                
            );
        }
        
		return (
			<div>
                {(this.state.TextDoc && this.state.targetPhraseData) ? 
                    <div style={{textAlign: "left", margin: "5%"}}>                    
                    <Highlighter
                        highlightClassName="YourHighlightClass"
                        searchWords={this.state.targetPhraseData.data}
                        autoEscape={true}
                        textToHighlight={this.state.TextDoc}
                        highlightTag={Highlight}
                    /> 
                    </div>
                    : console.log(this.state.TextDoc)
                
                }   
            </div>
	    );
      


    }
}

export default DisplayText;

// export default function DisplayText({TextArray}) {
//     return (
//         TextArray.map((Page) => 
//             Page.map((line)=>
//              <div style={{textAlign: "left", marginLeft: "5%"}} key={line[0]}> 
//                 {console.log(line.str)}
//                 {(line.str === " ") ? null : line.str}
//                 {(line.str === "\n") ? console.log("true") : console.log("false") }
//              </div>        
//             ) 
//         )
//     )
    
    
// }